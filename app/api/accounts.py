from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.session import SessionLocal
from app.schemas.account import AccountCreate, AccountRead
from app.services.account_service import AccountService


router = APIRouter(prefix="/accounts", tags=["Chart of Accounts"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/", response_model=AccountRead)
async def create_account(
    payload: AccountCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await AccountService.create_account(db, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[AccountRead])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    return await AccountService.list_accounts(db)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await AccountService.get_account(db, account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


from fastapi import Depends
from app.core.dependencies import get_current_user
from app.core.dependencies import admin_required

@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }


@router.get("/admin-test")
async def admin_test(current_user = Depends(admin_required)):
    return {"status": "admin access granted"}