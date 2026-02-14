from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.inventory_category import InventoryCategory
from app.models.account import Account
from app.schemas.inventory_category import InventoryCategoryCreate


async def create_inventory_category(
    db: AsyncSession,
    payload: InventoryCategoryCreate,
) -> InventoryCategory:

    # 1️⃣ Validate accounts exist
    account_ids = {
        payload.inventory_account_id,
        payload.cogs_account_id,
        payload.revenue_account_id,
        payload.gain_account_id,
        payload.loss_account_id,
    }

    result = await db.execute(
        select(Account).where(Account.id.in_(account_ids))
    )
    accounts = result.scalars().all()

    if len(accounts) != len(account_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more account IDs are invalid",
        )

    # 2️⃣ Create category
    category = InventoryCategory(
        code=payload.code,
        name=payload.name,
        inventory_account_id=payload.inventory_account_id,
        cogs_account_id=payload.cogs_account_id,
        revenue_account_id=payload.revenue_account_id,
        gain_account_id=payload.gain_account_id,
        loss_account_id=payload.loss_account_id,
        is_active=payload.is_active,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category