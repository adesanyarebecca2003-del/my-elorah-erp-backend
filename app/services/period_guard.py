from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.accounting_period import AccountingPeriod


async def ensure_period_open(db: AsyncSession, entry_date):
    result = await db.execute(
        select(AccountingPeriod)
        .where(AccountingPeriod.is_closed == True)
        .order_by(AccountingPeriod.end_date.desc())
        .limit(1)
    )
    closed_period = result.scalar_one_or_none()

    if closed_period and entry_date <= closed_period.end_date:
        raise ValueError("Posting into a closed accounting period is not allowed")