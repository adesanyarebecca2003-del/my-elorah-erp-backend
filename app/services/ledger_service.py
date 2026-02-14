from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.account import Account
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.schemas.ledger import LedgerResponse, AccountLedger, LedgerLine


def can_view_ledger():
    return True


def can_export_ledger():
    return True


async def generate_ledger(
    db: AsyncSession,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    exclude_closing: bool = False,
) -> LedgerResponse:

    if not can_view_ledger():
        raise ValueError("Permission denied")

    accounts_result = await db.execute(
        select(Account).where(
            Account.is_posting.is_(True),
            Account.is_active.is_(True)
        )
    )
    accounts = accounts_result.scalars().all()

    ledger_accounts: List[AccountLedger] = []

    for account in accounts:
        # Opening balance
        opening_query = (
            select(
                func.coalesce(func.sum(JournalLine.debit - JournalLine.credit), 0)
            )
            .join(JournalEntry)
            .where(
                JournalLine.account_id == account.id,
                JournalEntry.is_posted.is_(True),
                JournalEntry.entry_date < from_date if from_date else True
            )
        )

        opening_balance = Decimal(
            (await db.execute(opening_query)).scalar()
        )

        # Period movements
        movement_query = (
            select(
                JournalEntry.journal_number,
                JournalEntry.entry_date,
                JournalEntry.description,
                JournalLine.debit,
                JournalLine.credit
            )
            .join(JournalEntry)
            .where(
                JournalLine.account_id == account.id,
                JournalEntry.is_posted.is_(True),
                and_(
                    JournalEntry.entry_date >= from_date if from_date else True,
                    JournalEntry.entry_date <= to_date if to_date else True
                )
            )
            .order_by(JournalEntry.entry_date)
        )

        rows = (await db.execute(movement_query)).all()

        if opening_balance == 0 and not rows:
            continue

        balance = opening_balance
        lines: List[LedgerLine] = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        for r in rows:
            balance += Decimal(r.debit or 0) - Decimal(r.credit or 0)
            total_debit += Decimal(r.debit or 0)
            total_credit += Decimal(r.credit or 0)

            lines.append(
                LedgerLine(
                    journal_number=r.journal_number,
                    entry_date=r.entry_date,
                    description=r.description,
                    debit=Decimal(r.debit or 0),
                    credit=Decimal(r.credit or 0),
                    balance=balance,
                )
            )

        ledger_accounts.append(
            AccountLedger(
                account_code=account.code,
                account_name=account.name,
                opening_balance=opening_balance,
                total_debit=total_debit,
                total_credit=total_credit,
                closing_balance=balance,
                lines=lines,
            )
        )

    return LedgerResponse(
        from_date=from_date,
        to_date=to_date,
        accounts=ledger_accounts
    )

   
async def build_ledger(db: AsyncSession, from_date=None, to_date=None):
    stmt = (
        select(
            Account.code,
            Account.name,
            func.sum(JournalLine.debit).label("debit"),
            func.sum(JournalLine.credit).label("credit"),
        )
        .join(JournalLine, JournalLine.account_id == Account.id)
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .where(Account.is_posting == True)
        .group_by(Account.code, Account.name)
    )

    if from_date:
        stmt = stmt.where(JournalEntry.entry_date >= from_date)
    if to_date:
        stmt = stmt.where(JournalEntry.entry_date <= to_date)

    result = await db.execute(stmt)

    rows = []
    for r in result:
        balance = (r.debit or 0) - (r.credit or 0)
        rows.append([
            r.code,
            r.name,
            float(r.debit or 0),
            float(r.credit or 0),
            float(balance),
        ])

    return rows