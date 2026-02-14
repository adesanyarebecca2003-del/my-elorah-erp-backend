# app/schemas/inventory_sale.py
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import date

class InventorySaleLineCreate(BaseModel):
    product_id: UUID
    quantity: Decimal
    unit_price: Decimal


class InventorySaleCreate(BaseModel):
    sale_date: date
    customer: str
    amount_received: Decimal = Decimal("0.00")
    lines: list[InventorySaleLineCreate]