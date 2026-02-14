from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.inventory_valuation_service import generate_inventory_valuation
from app.schemas.inventory_valuation import InventoryValuationResponse
from app.utils.inventory_valuation_csv import export_inventory_valuation_csv
from app.utils.inventory_valuation_excel import export_inventory_valuation_excel
from app.core.permission import require_permission

router = APIRouter(
    prefix="/inventory-valuation",
    tags=["Inventory Valuation"]
)


@router.get("/", response_model=InventoryValuationResponse)
async def get_inventory_valuation(
    as_at: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.view"))
):
    return await generate_inventory_valuation(db, as_at)


@router.get("/export")
async def export_inventory_valuation(
    as_at: date = Query(...),
    format: str = Query("csv", enum=["csv", "excel"]),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.export"))
):
    valuation = await generate_inventory_valuation(db, as_at)

    if format == "excel":
        file = export_inventory_valuation_excel(valuation)
        return StreamingResponse(
            file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=inventory_valuation.xlsx"}
        )

    file = export_inventory_valuation_csv(valuation)
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_valuation.csv"}
    )