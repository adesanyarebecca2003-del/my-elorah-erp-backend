from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.accounting_period import (
    AccountingPeriodRead,
    AccountingPeriodCloseRequest,
)
from app.services.accounting_period_service import close_accounting_period
from app.models.accounting_period import AccountingPeriod
from app.core.dependencies import get_current_user, admin_required

router = APIRouter(
    prefix="/accounting-periods",
    tags=["Accounting Periods"],
)


@router.get("/", response_model=List[AccountingPeriodRead])
async def list_accounting_periods(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        AccountingPeriod.__table__.select().order_by(
            AccountingPeriod.start_date.desc()
        )
    )
    return result.mappings().all()


@router.post("/close")
async def close_period(
    payload: AccountingPeriodCloseRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required),
):
    try:
        return await close_accounting_period(
            db=db,
            start_date=payload.start_date,
            end_date=payload.end_date,
            closed_by=user.username,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))