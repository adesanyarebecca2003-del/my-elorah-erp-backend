from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class TrialBalanceRow(BaseModel):
    account_code: str
    account_name: str
    debit: Decimal
    credit: Decimal


class TrialBalanceResponse(BaseModel):
    as_at: date
    rows: List[TrialBalanceRow]
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool