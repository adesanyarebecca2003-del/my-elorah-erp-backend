from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel


class JournalEntryRead(BaseModel):
    id: UUID
    journal_number: str
    entry_date: date
    description: str
    is_posted: bool
    created_at: datetime

    class Config:
        from_attributes = True