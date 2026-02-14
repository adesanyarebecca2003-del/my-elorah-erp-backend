from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory_product import InventoryProduct
from app.models.inventory_category import InventoryCategory
from app.schemas.inventory_product import InventoryProductCreateSchema


async def create_inventory_product(
    db: AsyncSession,
    payload: InventoryProductCreateSchema,
) -> InventoryProduct:
    """
    Creates an inventory product (master data only).

    LOCKS ENFORCED:
    - Category must exist and be active
    - SKU must be unique
    - Product is created active by default
    """

    # 1️⃣ Resolve category
    result = await db.execute(
        select(InventoryCategory).where(
            InventoryCategory.code == payload.category_code,
            InventoryCategory.is_active.is_(True),
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or inactive category code: {payload.category_code}",
        )

    # 2️⃣ Enforce SKU uniqueness (defensive, DB still enforces)
    result = await db.execute(
        select(InventoryProduct).where(
            InventoryProduct.sku == payload.sku
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists",
        )

    # 3️⃣ Create product
    product = InventoryProduct(
        sku=payload.sku,
        name=payload.name,
        category_id=category.id,
        color=payload.color,
        length=payload.length,
        grams=payload.grams,
        size=payload.size,
        is_active=True,
    )

    # 4️⃣ Persist atomically
    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product