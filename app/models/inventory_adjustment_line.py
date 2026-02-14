from decimal import Decimal
import uuid

from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class InventoryAdjustmentLine(Base):
    __tablename__ = "inventory_adjustment_lines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    adjustment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_adjustments.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # REQUIRED for INCREASE, AUTO-DERIVED (FIFO) for DECREASE
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))

    fifo_cost_used: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))

    adjustment: Mapped["InventoryAdjustment"] = relationship(back_populates="lines")