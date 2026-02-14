from datetime import date
from typing import List
from pydantic import BaseModel
from decimal import Decimal


class InventoryValuationProduct(BaseModel):
    sku: str
    name: str
    quantity: Decimal
    value: Decimal
    unit_cost_avg: Decimal


class InventoryValuationCategory(BaseModel):
    category_code: str
    category_name: str
    quantity: Decimal
    value: Decimal
    products: List[InventoryValuationProduct]


class InventoryValuationResponse(BaseModel):
    as_at: date
    categories: List[InventoryValuationCategory]
    total_inventory_value: Decimal