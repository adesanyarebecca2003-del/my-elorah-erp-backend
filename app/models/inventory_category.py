from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from app.db.session import Base


class InventoryCategory(Base):
    __tablename__ = "inventory_categories"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    inventory_account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )
    cogs_account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )
    revenue_account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )
    gain_account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )
    loss_account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    products = relationship(
        "InventoryProduct",
        back_populates="category"
    )