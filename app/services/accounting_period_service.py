from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, datetime
from app.models.accounting_period import AccountingPeriod
from app.models.account import Account
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
import uuid


async def close_accounting_period(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    closed_by: str
):
    if start_date > end_date:
        raise ValueError("Invalid period date range")

    overlap = await db.execute(
        select(AccountingPeriod).where(
            AccountingPeriod.is_closed == True,
            AccountingPeriod.start_date <= end_date,
            AccountingPeriod.end_date >= start_date
        )
    )
    if overlap.scalars().first():
        raise ValueError("Period overlaps an already closed period")

    income_expense = await db.execute(
        select(Account)
        .where(Account.account_type.in_(["INCOME", "EXPENSE"]))
        .where(Account.is_posting == True)
    )
    accounts = income_expense.scalars().all()
    if not accounts:
        raise ValueError("No income or expense activity")

    closing_entry = JournalEntry(
        journal_number=f"CL-{start_date.strftime('%Y%m%d')}",
        entry_date=end_date,
        description="Period closing entry",
        is_posted=True
    )
    db.add(closing_entry)
    await db.flush()

    net_result = 0

    for acc in accounts:
        balance = acc.get_balance()  # assumed helper
        if balance == 0:
            continue

        if acc.account_type == "INCOME":
            net_result += balance
            db.add(JournalLine(
                entry_id=closing_entry.id,
                account_id=acc.id,
                debit=balance,
                credit=0
            ))
        else:
            net_result -= balance
            db.add(JournalLine(
                entry_id=closing_entry.id,
                account_id=acc.id,
                debit=0,
                credit=balance
            ))

    retained = await db.execute(
        select(Account).where(Account.code == "5030")
    )
    retained_account = retained.scalar_one()

    if net_result > 0:
        db.add(JournalLine(
            entry_id=closing_entry.id,
            account_id=retained_account.id,
            debit=0,
            credit=net_result
        ))
    else:
        db.add(JournalLine(
            entry_id=closing_entry.id,
            account_id=retained_account.id,
            debit=abs(net_result),
            credit=0
        ))

    period = AccountingPeriod(
        name=f"{start_date} to {end_date}",
        start_date=start_date,
        end_date=end_date,
        is_closed=True,
        closed_at=datetime.utcnow(),
        closed_by=closed_by
    )
    db.add(period)

    await db.commit()
    return {
        "period": period.name,
        "net_result": net_result
    }