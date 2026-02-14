from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.inventory_purchase import InventoryPurchaseCreate
from app.services.inventory_purchase_service import create_inventory_purchase
from app.core.permission import require_permission

router = APIRouter(prefix="/inventory/purchases", tags=["Purchases"])


@router.post("/")
async def create_purchase(
    payload: InventoryPurchaseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.purchase.create")),
):
    return await create_inventory_purchase(db, payload)
