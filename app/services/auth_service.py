from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.permission import Permission
from app.models.role import Role
from app.models.user_roles import UserRole
from app.models.role_permissions import RolePermission
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    hash_password,
)


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
):
    # Fetch user
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Resolve permissions via roles
    perm_result = await db.execute(
        select(Permission.code)
        .join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        )
        .join(
            UserRole,
            UserRole.role_id == RolePermission.role_id
        )
        .where(UserRole.user_id == user.id)
    )

    permission_codes = [row[0] for row in perm_result.all()]

    # Create JWT
    access_token = create_access_token(
        data={
            "sub": user.username,
            "is_admin": user.is_admin,
        }
    )

    return user, access_token


async def create_user_service(
    db: AsyncSession,
    username: str,
    password: str,
    is_admin: bool = False,
    permissions: str | None = None,
):
    # Ensure unique username
    result = await db.execute(select(User).where(User.username == username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=username,
        password_hash=hash_password(password),
        is_admin=is_admin,
        is_active=True,
        permissions=permissions,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user