from datetime import date
from decimal import Decimal
from typing import List
from pydantic import BaseModel


class IncomeStatementRow(BaseModel):
    section: str
    account_code: str
    account_name: str
    amount: Decimal


class IncomeStatementSection(BaseModel):
    name: str
    total: Decimal
    rows: List[IncomeStatementRow]


class IncomeStatementResponse(BaseModel):
    from_date: date
    to_date: date
    sections: List[IncomeStatementSection]
    net_profit: Decimal