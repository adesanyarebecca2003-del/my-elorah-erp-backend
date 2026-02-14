from datetime import date, datetime
from decimal import Decimal
from dateutil import parser as date_parser
from pydantic import BaseModel, Field, field_validator


class BulkPurchaseRow(BaseModel):
    purchase_date: date
    supplier: str
    product_sku: str
    quantity: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(gt=0)
    amount_paid: Decimal = Field(default=0)

    @field_validator("purchase_date", mode="before")
    @classmethod
    def parse_purchase_date(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            v = v.strip()

            # Accept ISO first
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue

        raise ValueError("purchase_date must be a valid date (e.g. 2026-02-12)")


class BulkSaleRow(BaseModel):
    sale_date: date
    customer: str
    product_sku: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    amount_received: Decimal = Decimal("0.00")

    @field_validator("sale_date", mode="before")
    @classmethod
    def parse_sale_date(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            try:
                return date_parser.parse(v, dayfirst=False).date()
            except Exception:
                pass

        raise ValueError("sale_date must be a valid date")