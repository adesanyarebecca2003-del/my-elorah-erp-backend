from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.db.session import Base


class InventoryPurchaseLine(Base):
    __tablename__ = "inventory_purchase_lines"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    purchase_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory_purchases.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory_products.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    purchase = relationship("InventoryPurchase", back_populates="lines")