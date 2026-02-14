from datetime import date
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permission import require_permission
from app.db.session import get_db
from app.services.ledger_service import generate_ledger
from app.schemas.ledger import LedgerResponse
from app.utils.csv_exporter import export_csv
from app.utils.excel_exporter import export_excel

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("/", response_model=LedgerResponse)
async def get_full_ledger(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await generate_ledger(db, from_date, to_date)


@router.get("/export")
async def export_ledger(
    format: Literal["csv", "excel"] = Query("csv"),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("ledger.export"))
):
    ledger = await generate_ledger(db, from_date, to_date)

    headers = ["Account Code", "Account Name", "Opening", "Debit", "Credit", "Closing"]
    rows = [
        [
            acc.account_code,
            acc.account_name,
            str(acc.opening_balance),
            str(acc.total_debit),
            str(acc.total_credit),
            str(acc.closing_balance),
        ]
        for acc in ledger.accounts
    ]

    if format == "excel":
        file = export_excel(headers, rows, "Ledger")
        return StreamingResponse(
            file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=ledger.xlsx"}
        )

    file = export_csv(headers, rows)
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ledger.csv"}
    )


@router.get("/{account_code}")
async def get_single_account_ledger(
    account_code: str,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    ledger = await generate_ledger(db, from_date, to_date)
    for acc in ledger.accounts:
        if acc.account_code == account_code:
            return acc
    return {"message": "No entries found"}