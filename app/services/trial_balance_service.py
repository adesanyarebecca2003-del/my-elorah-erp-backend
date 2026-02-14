from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.account import Account
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.schemas.trial_balance import TrialBalanceResponse, TrialBalanceRow


def can_view_trial_balance():
    return True


def can_export_trial_balance():
    return True


async def generate_trial_balance(
    db: AsyncSession,
    as_at: date,
    exclude_closing: bool = False,
) -> TrialBalanceResponse:

    if not can_view_trial_balance():
        raise ValueError("Permission denied")

    accounts_result = await db.execute(
        select(Account).where(
            Account.is_posting.is_(True),
            Account.is_active.is_(True)
        )
    )
    accounts = accounts_result.scalars().all()

    rows: List[TrialBalanceRow] = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

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

        debit = Decimal("0.00")
        credit = Decimal("0.00")

        if balance > 0:
            debit = balance
            total_debit += debit
        elif balance < 0:
            credit = abs(balance)
            total_credit += credit
        else:
            continue

        rows.append(
            TrialBalanceRow(
                account_code=account.code,
                account_name=account.name,
                debit=debit,
                credit=credit,
            )
        )

    return TrialBalanceResponse(
        as_at=as_at,
        rows=rows,
        total_debit=total_debit,
        total_credit=total_credit,
        is_balanced=total_debit == total_credit,
    )


async def build_trial_balance(db):
    ledger = await build_ledger(db)

    rows = []
    total_debit = 0
    total_credit = 0

    for code, name, debit, credit, balance in ledger:
        if balance > 0:
            rows.append([code, name, balance, 0])
            total_debit += balance
        else:
            rows.append([code, name, 0, abs(balance)])
            total_credit += abs(balance)

    return rows, total_debit, total_credit