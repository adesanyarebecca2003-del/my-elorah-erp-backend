from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class AccountingPeriodRead(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date
    is_closed: bool
    closed_at: Optional[datetime]
    closed_by: Optional[str]

    class Config:
        from_attributes = True


class AccountingPeriodCloseRequest(BaseModel):
    start_date: date
    end_date: date