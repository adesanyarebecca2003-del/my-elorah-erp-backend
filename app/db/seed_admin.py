import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.services.auth_service import create_user


async def seed():
    async with SessionLocal() as db:
        await create_user(
            db=db,
            username="admin",
            password="Admin@1234",
            is_admin=True,
            permissions=None,
        )
        print("✅ Admin user created")

if __name__ == "__main__":
    asyncio.run(seed())