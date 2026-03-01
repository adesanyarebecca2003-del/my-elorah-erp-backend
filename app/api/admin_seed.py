from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import admin_required

# import your seeder here (adjust import if your path differs)
from app.db.seed_chart_of_accounts import seed

router = APIRouter(prefix="/admin/seed", tags=["Admin Seed"])


@router.post("/chart-of-accounts")
async def seed_coa(
    db: AsyncSession = Depends(get_db),
    _admin = Depends(admin_required),
):
    # Run your seeding function
    await seed(db)
    return {"detail": "Chart of Accounts seeded successfully"}