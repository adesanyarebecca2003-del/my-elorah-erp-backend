from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class InventoryProduct(Base):
    __tablename__ = "inventory_products"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    category_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_categories.id"),
        nullable=False
    )

    color: Mapped[str | None] = mapped_column(String(50))
    length: Mapped[str | None] = mapped_column(String(50))
    grams: Mapped[str | None] = mapped_column(String(50))
    size: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    category = relationship(
        "InventoryCategory",
        back_populates="products"
    )