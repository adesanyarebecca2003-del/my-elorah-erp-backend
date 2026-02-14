from datetime import date
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.account import Account
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.schemas.balance_sheet import (
    BalanceSheetResponse,
    BalanceSheetSection,
    BalanceSheetRow,
)


def can_view_balance_sheet():
    return True


def can_export_balance_sheet():
    return True


def classify_section(account: Account):
    if account.account_type == "ASSET":
        section = "Assets"
    elif account.account_type == "LIABILITY":
        section = "Liabilities"
    else:
        section = "Equity"

    subsection = "Current" if account.is_current else "Non-current"
    return section, subsection


async def generate_balance_sheet(
    db: AsyncSession,
    as_at: date,
) -> BalanceSheetResponse:

    if not can_view_balance_sheet():
        raise ValueError("Permission denied")

    result = await db.execute(
        select(Account).where(
            Account.account_type.in_(["ASSET", "LIABILITY", "EQUITY"]),
            Account.is_posting.is_(True),
            Account.is_active.is_(True),
        )
    )
    accounts = result.scalars().all()

    buckets = {
        "Assets": defaultdict(list),
        "Liabilities": defaultdict(list),
        "Equity": defaultdict(list),
    }

    totals = {
        "Assets": Decimal("0.00"),
        "Liabilities": Decimal("0.00"),
        "Equity": Decimal("0.00"),
    }

    for account in accounts:
        balance_query = (
            select(
                func.coalesce(func.sum(JournalLine.debit - JournalLine.credit), 0)
            )
            .join(JournalEntry)
            .where(
                JournalLine.account_id == account.id,
                JournalEntry.is_posted.is_(True),
                JournalEntry.entry_date <= as_at,
            )
        )

        balance = Decimal((await db.execute(balance_query)).scalar())

        if balance == 0:
            continue

        if account.account_type in ["LIABILITY", "EQUITY"]:
            balance = balance * Decimal("-1")

        section, subsection = classify_section(account)

        buckets[section][subsection].append(
            BalanceSheetRow(
                section=section,
                subsection=subsection,
                account_code=account.code,
                account_name=account.name,
                balance=balance,
            )
        )

        totals[section] += balance

    assets_section = BalanceSheetSection(
        name="Assets",
        total=totals["Assets"],
        rows=[
            row
            for rows in buckets["Assets"].values()
            for row in rows
        ],
    )

    liabilities_section = BalanceSheetSection(
        name="Liabilities",
        total=totals["Liabilities"],
        rows=[
            row
            for rows in buckets["Liabilities"].values()
            for row in rows
        ],
    )

    equity_section = BalanceSheetSection(
        name="Equity",
        total=totals["Equity"],
        rows=[
            row
            for rows in buckets["Equity"].values()
            for row in rows
        ],
    )

    balances = totals["Assets"] == (totals["Liabilities"] + totals["Equity"])

    return BalanceSheetResponse(
        as_at=as_at,
        assets=assets_section,
        liabilities=liabilities_section,
        equity=equity_section,
        total_assets=totals["Assets"],
        total_liabilities=totals["Liabilities"],
        total_equity=totals["Equity"],
        balances=balances,
    )


async def build_balance_sheet(db, as_at):
    ledger = await build_ledger(db, to_date=as_at)

    assets = []
    liabilities = []
    equity = []

    for code, name, debit, credit, balance in ledger:
        if code.startswith("1") or code.startswith("2"):
            assets.append([code, name, balance])
        elif code.startswith("3") or code.startswith("4"):
            liabilities.append([code, name, abs(balance)])
        elif code.startswith("5"):
            equity.append([code, name, abs(balance)])

    return assets, liabilities, equity