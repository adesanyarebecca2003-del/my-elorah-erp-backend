from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class InventoryCategoryResponse(BaseModel):
    id: UUID
    code: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryCategoryCreate(BaseModel):
    code: str
    name: str

    inventory_account_id: UUID
    cogs_account_id: UUID
    revenue_account_id: UUID
    gain_account_id: UUID
    loss_account_id: UUID

    is_active: bool = True