from pydantic import BaseModel, Field
from typing import Optional


class InventoryProductCreateSchema(BaseModel):
    sku: str = Field(..., max_length=50)
    name: str = Field(..., max_length=150)
    category_code: str = Field(..., max_length=50)

    color: Optional[str] = Field(default=None, max_length=50)
    length: Optional[str] = Field(default=None, max_length=50)
    grams: Optional[str] = Field(default=None, max_length=50)
    size: Optional[str] = Field(default=None, max_length=50)