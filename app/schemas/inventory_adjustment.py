# app/schemas/inventory_adjustment.py
from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID
from datetime import date
from typing import Literal

class InventoryAdjustmentLineCreate(BaseModel):
    product_id: UUID
    quantity: Decimal
    unit_cost: Decimal | None = None  # required for INCREASE


class InventoryAdjustmentCreate(BaseModel):
    adjustment_date: date
    reason: str
    adjustment_type: Literal["INCREASE", "DECREASE"]
    lines: list[InventoryAdjustmentLineCreate]