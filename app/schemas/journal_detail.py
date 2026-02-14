from pydantic import BaseModel
from typing import List
from datetime import date
from uuid import UUID


class JournalLineRead(BaseModel):
    account_code: str
    debit: float
    credit: float


class JournalDetailRead(BaseModel):
    id: UUID
    journal_number: str
    entry_date: date
    description: str
    is_posted: bool
    lines: List[JournalLineRead]

    class Config:
        from_attributes = True