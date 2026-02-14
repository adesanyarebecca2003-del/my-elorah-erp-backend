from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.inventory_product import InventoryProduct
from app.models.inventory_category import InventoryCategory
from app.schemas.inventory_product import InventoryProductCreateSchema
from app.services.inventory_product_service import create_inventory_product
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/inventory/products",
    tags=["Inventory Products"],
)


# ===============================
# CREATE PRODUCT (ADMIN ONLY)
# ===============================
@router.post(
    "/",
    summary="Create inventory product",
)
async def create_product(
    payload: InventoryProductCreateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    product = await create_inventory_product(db, payload)

    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "category_id": product.category_id,
        "is_active": product.is_active,
    }


# ===============================
# LIST PRODUCTS (ADMIN ONLY)
# ===============================
@router.get(
    "/",
    summary="List inventory products",
)
async def list_products(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    result = await db.execute(
        select(
            InventoryProduct.id,
            InventoryProduct.sku,
            InventoryProduct.name,
            InventoryProduct.color,
            InventoryProduct.length,
            InventoryProduct.grams,
            InventoryProduct.size,
            InventoryProduct.is_active,
            InventoryProduct.created_at,
            InventoryCategory.code.label("category_code"),
            InventoryCategory.name.label("category_name"),
        )
        .join(
            InventoryCategory,
            InventoryProduct.category_id == InventoryCategory.id,
        )
        .order_by(InventoryProduct.created_at.desc())
    )

    return [
        {
            "id": r.id,
            "sku": r.sku,
            "name": r.name,
            "category_code": r.category_code,
            "category_name": r.category_name,
            "color": r.color,
            "length": r.length,
            "grams": r.grams,
            "size": r.size,
            "is_active": r.is_active,
            "created_at": r.created_at,
        }
        for r in result.all()
    ]