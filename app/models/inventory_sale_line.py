from decimal import Decimal
import uuid

from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class InventorySaleLine(Base):
    __tablename__ = "inventory_sale_lines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_sales.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    fifo_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))

    sale: Mapped["InventorySale"] = relationship(back_populates="lines")

    product: Mapped["InventoryProduct"] = relationship("InventoryProduct")