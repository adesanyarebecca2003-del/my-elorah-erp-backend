from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class NormalBalance(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class AccountBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str
    account_type: AccountType
    normal_balance: NormalBalance
    parent_id: Optional[UUID]
    is_posting: bool = True
    is_active: bool = True
    is_current: Optional[bool]


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: UUID
    is_system_locked: bool

    class Config:
        from_attributes = True


class AccountTree(AccountRead):
    children: List["AccountTree"] = []

    class Config:
        from_attributes = True