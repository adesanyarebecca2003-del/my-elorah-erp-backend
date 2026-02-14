from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.permission import require_permission
from app.services.trial_balance_service import generate_trial_balance
from app.utils.csv_exporter import export_csv
from app.utils.excel_exporter import export_excel

router = APIRouter(
    prefix="/trial-balance",
    tags=["Trial Balance"]
)


@router.get("/")
async def get_trial_balance(
    as_at: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("trial_balance.view"))
):
    """
    JSON trial balance (for UI or API use)
    """
    return await generate_trial_balance(db, as_at)


@router.get("/export")
async def export_trial_balance(
    as_at: date = Query(...),
    format: str = Query("csv", enum=["csv", "excel"]),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("trial_balance.export"))
):
    tb = await generate_trial_balance(db, as_at)

    headers = ["Account Code", "Account Name", "Debit", "Credit"]
    rows = [
        [
            r.account_code,
            r.account_name,
            str(r.debit),
            str(r.credit),
        ]
        for r in tb.rows
    ]

    if format == "excel":
        file = export_excel(headers, rows, "trial_balance")
        return StreamingResponse(
            file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=trial_balance.xlsx"}
        )

    file = export_csv(headers, rows)
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trial_balance.csv"}
    )