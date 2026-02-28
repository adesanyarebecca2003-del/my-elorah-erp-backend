import os
from pydantic import BaseModel
from sqlalchemy import select
from fastapi import HTTPException
from app.models.user import User
from app.core.security import hash_password

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth_service import authenticate_user
from app.schemas.auth import LoginSchema, TokenResponse
from app.schemas.auth import UserCreateSchema
from app.services.auth_service import create_user_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginSchema,
    db: AsyncSession = Depends(get_db)
):
    user, token = await authenticate_user(
        db=db,
        username=data.username,
        password=data.password
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "is_admin": user.is_admin,
        "permissions": []
    }


from fastapi import Depends
from app.core.dependencies import get_current_user


@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }

@router.post("/users")
async def create_user(
    payload: UserCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Admin-only
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await create_user_service(
        db=db,
        username=payload.username,
        password=payload.password,
        is_admin=payload.is_admin,
        permissions=payload.permissions,
    )

    return {
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "permissions": getattr(user, "permissions", None),
    }

class BootstrapUserSchema(BaseModel):
    bootstrap_key: str
    username: str
    password: str
    is_admin: bool = True
    permissions: str | None = "*"


@router.post("/bootstrap-user")
async def bootstrap_user(
    payload: BootstrapUserSchema,
    db: AsyncSession = Depends(get_db),
):
    key = os.getenv("BOOTSTRAP_KEY")
    if not key or payload.bootstrap_key != key:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if user:
        user.password_hash = hash_password(payload.password)
        user.is_admin = payload.is_admin
        if hasattr(user, "permissions"):
            user.permissions = payload.permissions
    else:
        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            is_admin=payload.is_admin,
            is_active=True,
        )
        if hasattr(user, "permissions"):
            user.permissions = payload.permissions
        db.add(user)

    await db.commit()
    return {"detail": "Bootstrap user created/updated"}