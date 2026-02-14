from fastapi import APIRouter, Depends, Query
from app.db.session import get_db
from app.exports.csv_export import export_csv
from app.exports.excel_export import export_excel
from app.services.ledger_service import build_ledger

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/ledger")
async def download_ledger(
    format: str = Query("csv"),
    db=Depends(get_db)
):
    rows = await build_ledger(db)
    headers = ["Code", "Account", "Debit", "Credit", "Balance"]

    if format == "excel":
        return export_excel("ledger.xlsx", headers, rows)

    return export_csv("ledger.csv", headers, rows)