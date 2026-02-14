import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User

ADMIN_PERMISSIONS = [
    "inventory.purchase.create",
    "inventory.purchase.bulk_upload",
    "inventory.sale.create",
    "inventory.sale.bulk_upload",
]

async def run():
    async with SessionLocal() as db:  # type: AsyncSession
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        admin = result.scalar_one_or_none()

        if not admin:
            print("❌ Admin user not found")
            return

        admin.permissions = ADMIN_PERMISSIONS
        admin.is_admin = True

        await db.commit()

        print("✅ Admin permissions updated:")
        for p in ADMIN_PERMISSIONS:
            print("  -", p)

if __name__ == "__main__":
    asyncio.run(run())