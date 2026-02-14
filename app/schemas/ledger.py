from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class LedgerLine(BaseModel):
    journal_number: str
    entry_date: date
    description: Optional[str]
    debit: Decimal
    credit: Decimal
    balance: Decimal


class AccountLedger(BaseModel):
    account_code: str
    account_name: str
    opening_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    closing_balance: Decimal
    lines: List[LedgerLine]


class LedgerResponse(BaseModel):
    from_date: Optional[date]
    to_date: Optional[date]
    accounts: List[AccountLedger]