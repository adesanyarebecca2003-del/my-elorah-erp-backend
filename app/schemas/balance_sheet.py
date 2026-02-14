from datetime import date
from decimal import Decimal
from typing import List
from pydantic import BaseModel


class BalanceSheetRow(BaseModel):
    section: str
    subsection: str
    account_code: str
    account_name: str
    balance: Decimal


class BalanceSheetSection(BaseModel):
    name: str
    total: Decimal
    rows: List[BalanceSheetRow]


class BalanceSheetResponse(BaseModel):
    as_at: date
    assets: BalanceSheetSection
    liabilities: BalanceSheetSection
    equity: BalanceSheetSection
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    balances: bool