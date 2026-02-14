from datetime import date
from typing import List
from pydantic import BaseModel, Field

from app.schemas.journal_line import JournalLineCreate


class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str
    lines: List[JournalLineCreate] = Field(min_length=2)