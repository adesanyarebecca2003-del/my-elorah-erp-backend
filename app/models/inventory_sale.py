from datetime import date
import uuid
from sqlalchemy import ForeignKey

from sqlalchemy import Date, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class InventorySale(Base):
    __tablename__ = "inventory_sales"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer: Mapped[str | None] = mapped_column(String(255))
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)

    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id"),
        nullable=True,
    )

    lines: Mapped[list["InventorySaleLine"]] = relationship(
        back_populates="sale",
        cascade="all, delete-orphan"
    )