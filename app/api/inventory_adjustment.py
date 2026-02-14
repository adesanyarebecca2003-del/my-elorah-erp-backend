# app/api/inventory_adjustment.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.inventory_adjustment import InventoryAdjustmentCreate
from app.services.inventory_adjustment_service import create_inventory_adjustment
from app.core.permission import require_permission

router = APIRouter(prefix="/inventory/adjustments", tags=["Inventory Adjustment"])


@router.post("/")
async def create_adjustment(
    payload: InventoryAdjustmentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.adjustment.create")),
):
    return await create_inventory_adjustment(db, payload)