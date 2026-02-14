from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.permission import require_permission
from app.services.income_statement_service import generate_income_statement
from app.utils.csv_exporter import export_csv
from app.utils.excel_exporter import export_excel
from app.schemas.income_statement import IncomeStatementResponse

router = APIRouter(
    prefix="/income-statement",
    tags=["Income Statement"]
)


@router.get("/", response_model=IncomeStatementResponse)
async def get_income_statement(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("income_statement.view")),
):
    return await generate_income_statement(db, from_date, to_date)


@router.get("/export")
async def export_income_statement(
    from_date: date = Query(...),
    to_date: date = Query(...),
    format: str = Query("csv", enum=["csv", "excel"]),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("income_statement.export")),
):
    report = await generate_income_statement(db, from_date, to_date)

    headers = ["Section", "Account Code", "Account Name", "Amount"]
    rows = []

    for section in report.sections:
        for r in section.rows:
            rows.append([section.name, r.account_code, r.account_name, str(r.amount)])

        # section total row
        rows.append([section.name, "", "TOTAL", str(section.total)])
        rows.append(["", "", "", ""])  # spacer

    # net profit at end
    rows.append(["", "", "NET PROFIT", str(report.net_profit)])

    if format == "excel":
        file = export_excel(headers, rows, "income_statement")
        return StreamingResponse(
            file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=income_statement.xlsx"},
        )

    file = export_csv(headers, rows)
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=income_statement.csv"},
    )
