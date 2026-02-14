from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.db.session import Base


class InventoryPurchase(Base):
    __tablename__ = "inventory_purchases"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    supplier: Mapped[str] = mapped_column(String(150), nullable=False)

    freight_cost: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    amount_paid: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    lines = relationship(
        "InventoryPurchaseLine",
        back_populates="purchase",
        cascade="all, delete-orphan"
    )