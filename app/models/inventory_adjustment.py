from datetime import date
import uuid

from sqlalchemy import Date, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    adjustment_date: Mapped[date] = mapped_column(Date, nullable=False)

    adjustment_type: Mapped[str] = mapped_column(
        Enum("INCREASE", "DECREASE", name="inventory_adjustment_type"),
        nullable=False
    )

    reason: Mapped[str | None] = mapped_column(String(255))

    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)

    lines: Mapped[list["InventoryAdjustmentLine"]] = relationship(
        back_populates="adjustment",
        cascade="all, delete-orphan"
    )