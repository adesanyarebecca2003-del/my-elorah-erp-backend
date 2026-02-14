# app/api/inventory_sale_return.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.inventory_sale_return import InventorySaleReturnCreate
from app.services.inventory_sale_return_service import create_inventory_sale_return
from app.core.permission import require_permission

router = APIRouter(prefix="/inventory/sales-returns", tags=["Sales Return"])


@router.post("/")
async def create_sale_return(
    payload: InventorySaleReturnCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.sale_return.create")),
):
    return await create_inventory_sale_return(db, payload)