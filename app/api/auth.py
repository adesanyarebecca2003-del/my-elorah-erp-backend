from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth_service import authenticate_user
from app.schemas.auth import LoginSchema, TokenResponse

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