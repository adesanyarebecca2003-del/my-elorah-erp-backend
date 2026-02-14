from decimal import Decimal
import uuid

from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class InventorySaleReturnLine(Base):
    __tablename__ = "inventory_sale_return_lines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    return_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_sale_returns.id", ondelete="CASCADE"),
        nullable=False
    )

    # NEW: links return to original sale line
    sale_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_sale_lines.id"),
        nullable=True  # matches migration for now
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    fifo_reversal_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    sale_return: Mapped["InventorySaleReturn"] = relationship(back_populates="lines")