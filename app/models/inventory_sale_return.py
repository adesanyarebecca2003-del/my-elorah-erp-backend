from datetime import date
import uuid

from sqlalchemy import Date, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class InventorySaleReturn(Base):
    __tablename__ = "inventory_sale_returns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer: Mapped[str | None] = mapped_column(String(255))
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)

    lines: Mapped[list["InventorySaleReturnLine"]] = relationship(
        back_populates="sale_return",
        cascade="all, delete-orphan"
    )