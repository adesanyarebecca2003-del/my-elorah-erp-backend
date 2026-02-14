from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.permission import require_permission
from app.services.balance_sheet_service import generate_balance_sheet
from app.utils.csv_exporter import export_csv
from app.utils.excel_exporter import export_excel
from app.schemas.balance_sheet import BalanceSheetResponse

router = APIRouter(
    prefix="/balance-sheet",
    tags=["Statement of Financial Position"]
)


@router.get("/", response_model=BalanceSheetResponse)
async def get_balance_sheet(
    as_at: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await generate_balance_sheet(db, as_at)


@router.get("/export")
async def export_balance_sheet(
    as_at: date = Query(...),
    format: Literal["csv", "excel"] = Query("csv"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("balance_sheet.export"))
):
    """
    Download balance sheet as CSV or Excel
    """
    bs = await generate_balance_sheet(db, as_at)

    # Flatten: assets + liabilities + equity
    headers = ["Section", "Subsection", "Account Code", "Account Name", "Balance"]
    rows = []

    for section in [bs.assets, bs.liabilities, bs.equity]:
        for r in section.rows:
            rows.append([
                r.section,
                r.subsection,
                r.account_code,
                r.account_name,
                str(r.balance),
            ])

    if format == "excel":
        file = export_excel(headers, rows, "balance_sheet")
        return StreamingResponse(
            file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=balance_sheet.xlsx"}
        )

    file = export_csv(headers, rows)
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=balance_sheet.csv"}
    )