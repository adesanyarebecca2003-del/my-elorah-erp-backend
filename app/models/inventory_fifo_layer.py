from datetime import date
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.session import Base


class InventoryFIFOLayer(Base):
    __tablename__ = "inventory_fifo_layers"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_products.id"),
        nullable=False,
    )
    purchase_line_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_purchase_lines.id"),
        nullable=False,
    )

    received_date: Mapped[date] = mapped_column(Date, nullable=False)

    quantity_in: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_out: Mapped[int] = mapped_column(Integer, default=0)

    unit_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    @hybrid_property
    def remaining_quantity(self) -> int:
        """
        Remaining units in this FIFO layer (Python instance usage).
        Safe for normal code: layer.remaining_quantity
        """
        qin = self.quantity_in or 0
        qout = self.quantity_out or 0
        return qin - qout

    @remaining_quantity.expression
    def remaining_quantity(cls):
        """
        Remaining units in this FIFO layer (SQL usage).
        Safe for queries: InventoryFIFOLayer.remaining_quantity > 0
        """
        return cls.quantity_in - cls.quantity_out