import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AccountType(enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class NormalBalance(enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)

    account_type = Column(Enum(AccountType), nullable=False)
    normal_balance = Column(Enum(NormalBalance), nullable=False)

    parent_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)

    is_posting = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_system_locked = Column(Boolean, nullable=False, default=False)

    is_current = Column(Boolean, nullable=True)  # only for balance sheet accounts

    parent = relationship(
        "Account",
        remote_side=[id],
        backref="children",
    )

    __table_args__ = (
        UniqueConstraint("code", name="uq_account_code"),
        UniqueConstraint("name", name="uq_account_name"),
    )