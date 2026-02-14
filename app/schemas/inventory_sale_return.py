from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class InventorySaleReturnLineCreate(BaseModel):
    sale_line_id: UUID
    quantity: int = Field(gt=0)

    @field_validator("quantity", mode="before")
    @classmethod
    def parse_quantity(cls, v):
        # Accept "2", 2, 2.0, Decimal("2") etc.
        q = int(Decimal(str(v)))
        if q <= 0:
            raise ValueError("quantity must be at least 1")
        return q


class InventorySaleReturnCreate(BaseModel):
    return_date: date
    customer: str = Field(min_length=1)
    amount_refunded: Decimal = Decimal("0.00")
    lines: list[InventorySaleReturnLineCreate]

    @field_validator("lines")
    @classmethod
    def lines_not_empty(cls, v):
        if not v:
            raise ValueError("At least one return line is required")
        return v
