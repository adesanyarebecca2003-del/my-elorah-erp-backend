from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.inventory_category import InventoryCategory
from app.schemas.inventory_category import (
    InventoryCategoryCreate,
    InventoryCategoryResponse,
)
from app.services.inventory_category_service import create_inventory_category

router = APIRouter(
    prefix="/inventory/categories",
    tags=["Inventory Categories"],
)


@router.get("/", response_model=list[InventoryCategoryResponse])
async def list_inventory_categories(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InventoryCategory)
        .order_by(InventoryCategory.created_at.desc())
    )
    return result.scalars().all()


@router.post(
    "/",
    response_model=InventoryCategoryResponse,
    status_code=201,
)
async def create_inventory_category_api(
    payload: InventoryCategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_inventory_category(db, payload)