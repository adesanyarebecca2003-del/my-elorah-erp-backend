from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile

from app.models import InventoryProduct
from decimal import Decimal
from app.schemas.inventory_sale import InventorySaleCreate, InventorySaleLineCreate
from app.utils.csv_parser import parse_csv
from app.utils.excel_parser import parse_excel
from app.schemas.inventory_bulk_upload import BulkPurchaseRow, BulkSaleRow
from app.schemas.inventory_purchase import (
    InventoryPurchaseCreate,
    InventoryPurchaseLineCreate,
)
from app.services.inventory_purchase_service import create_inventory_purchase
from app.services.inventory_sale_service import create_inventory_sale
from app.services.period_guard import ensure_period_open


async def _parse_file(file: UploadFile):
    filename = (file.filename or "").lower()

    if filename.endswith(".csv"):
        return parse_csv(file)

    if filename.endswith(".xlsx"):
        return parse_excel(file)

    raise ValueError("Unsupported file format. Please upload .csv or .xlsx")


async def bulk_upload_purchases(db: AsyncSession, file: UploadFile):
    raw_rows = await _parse_file(file)

    # 1) Validate & coerce
    rows = [BulkPurchaseRow(**r) for r in raw_rows]

    if not rows:
        return {"status": "No rows found in file", "count": 0, "purchases_created": 0}

    # 2) Period validation (fail fast)
    for r in rows:
        await ensure_period_open(db, r.purchase_date)

    # 3) Process EACH ROW as ONE PURCHASE (no grouping)
    created = 0

    for r in rows:
        # Normalize text to avoid hidden spaces causing lookup issues
        supplier = r.supplier.strip()
        sku = r.product_sku.strip()

        product = await db.scalar(
            select(InventoryProduct).where(InventoryProduct.sku == sku)
        )
        if not product:
            raise ValueError(f"Invalid product SKU: {sku}")

        payload = InventoryPurchaseCreate(
            purchase_date=r.purchase_date,
            supplier=supplier,
            amount_paid=r.amount_paid,
            lines=[
                InventoryPurchaseLineCreate(
                    product_id=product.id,
                    quantity=r.quantity,
                    unit_cost=r.unit_cost,
                )
            ],
        )

        await create_inventory_purchase(db, payload)
        created += 1

    return {
        "status": "Bulk purchases uploaded successfully",
        "count": len(rows),
        "purchases_created": created,
    }


async def bulk_upload_sales(db: AsyncSession, file: UploadFile):
    raw_rows = await _parse_file(file)

    # 1) Validate & coerce
    rows = [BulkSaleRow(**r) for r in raw_rows]

    if not rows:
        return {"status": "No rows found in file", "count": 0, "sales_created": 0}

    # 2) Period validation (fail fast)
    for r in rows:
        await ensure_period_open(db, r.sale_date)

    created = 0

    # 3) Process EACH ROW as ONE SALE (no grouping)
    for r in rows:
        customer = (r.customer or "").strip()
        sku = (r.product_sku or "").strip()

        product = await db.scalar(
            select(InventoryProduct).where(InventoryProduct.sku == sku)
        )
        if not product:
            raise ValueError(f"Invalid product SKU: {sku}")

        # Build payload in the shape create_inventory_sale expects
        payload = {
            "sale_date": r.sale_date,
            "customer": customer,
            "amount_received": r.amount_received,
            "lines": [
                {
                    "product_id": product.id,
                    "quantity": r.quantity,
                    "unit_price": r.unit_price,
                }
            ],
            # Optional: if you later add this to BulkSaleRow, it will be picked up
            # "amount_received": r.amount_received,
        }

        await create_inventory_sale(db, payload)
        created += 1

    return {
        "status": "Bulk sales uploaded successfully",
        "count": len(rows),
        "sales_created": created,
    }