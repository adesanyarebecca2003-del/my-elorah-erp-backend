import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.session import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    description: Mapped[str] = mapped_column(String(255))
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lines = relationship(
        "JournalLine",
        back_populates="entry",
        cascade="all, delete-orphan"
    )