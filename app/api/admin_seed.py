from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import admin_required

# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.db.session import get_db
# from app.core.dependencies import admin_required
# from app.db.seed_chart_of_accounts import seed
#
# router = APIRouter(prefix="/admin/seed", tags=["Admin Seed"])
#
# @router.post("/chart-of-accounts")
# async def seed_coa(
#     db: AsyncSession = Depends(get_db),
#     _admin = Depends(admin_required),
# ):
#     result = seed()
#     if hasattr(result, "__await__"):
#         await result
#     return {"detail": "Chart of Accounts seeded successfully"}