from datetime import date
from typing import List
from pydantic import BaseModel, Field

from app.schemas.journal_line import JournalLinePost


class JournalEntryPost(BaseModel):
    entry_date: date
    description: str
    lines: List[JournalLinePost] = Field(min_length=2)