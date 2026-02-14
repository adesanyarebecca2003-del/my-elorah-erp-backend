# app/api/inventory_sale.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.inventory_sale import InventorySaleCreate
from app.services.inventory_sale_service import create_inventory_sale
from app.core.permission import require_permission

router = APIRouter(prefix="/inventory/sales", tags=["Sales Revenue"])


@router.post("/")
async def create_sale(
    payload: InventorySaleCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.sale.create")),
):
    return await create_inventory_sale(db, payload)