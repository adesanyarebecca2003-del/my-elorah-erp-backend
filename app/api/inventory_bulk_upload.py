from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.permission import require_permission
from app.services.inventory_bulk_upload_service import (
    bulk_upload_purchases,
    bulk_upload_sales
)

router = APIRouter(prefix="/inventory/bulk-upload", tags=["Inventory Bulk Upload"])


@router.post("/purchases")
async def upload_purchases(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.purchase.bulk_upload"))
):
    return await bulk_upload_purchases(db, file)


@router.post("/sales")
async def upload_sales(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("inventory.sale.bulk_upload"))
):
    return await bulk_upload_sales(db, file)