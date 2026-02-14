from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import date


class InventoryPurchaseLineCreate(BaseModel):
    product_id: UUID
    quantity: Decimal
    unit_cost: Decimal


class InventoryPurchaseCreate(BaseModel):
    purchase_date: date
    supplier: str
    amount_paid: Decimal
    lines: list[InventoryPurchaseLineCreate]