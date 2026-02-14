from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.account import Account


class AccountService:

    @staticmethod
    async def create_account(db: AsyncSession, data: dict) -> Account:
        # Parent must exist if provided
        parent_id = data.get("parent_id")
        if parent_id:
            parent = await db.get(Account, parent_id)
            if not parent:
                raise ValueError("Parent account does not exist")
            if parent.is_posting:
                raise ValueError("Parent account cannot be a posting account")

        # Unique code
        exists = await db.execute(
            select(Account).where(Account.code == data["code"])
        )
        if exists.scalar_one_or_none():
            raise ValueError("Account code already exists")

        # Unique name
        exists = await db.execute(
            select(Account).where(Account.name == data["name"])
        )
        if exists.scalar_one_or_none():
            raise ValueError("Account name already exists")

        account = Account(**data)
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def list_accounts(db: AsyncSession):
        result = await db.execute(select(Account))
        return result.scalars().all()

    @staticmethod
    async def get_account(db: AsyncSession, account_id: UUID):
        account = await db.get(Account, account_id)
        if not account:
            raise ValueError("Account not found")
        return account