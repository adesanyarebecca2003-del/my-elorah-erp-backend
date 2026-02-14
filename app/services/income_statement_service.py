from datetime import date
from decimal import Decimal
from collections import defaultdict
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.account import Account
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.schemas.income_statement import (
    IncomeStatementResponse,
    IncomeStatementSection,
    IncomeStatementRow,
)


def can_view_income_statement():
    return True


def can_export_income_statement():
    return True


def classify_section(account_code: str) -> str:
    if account_code.startswith("60"):
        return "Revenue"
    if account_code.startswith("61"):
        return "Sales Returns"
    if account_code.startswith("62") or account_code.startswith("63"):
        return "Other Income"
    if account_code.startswith("70"):
        return "Cost of Sales"
    if account_code.startswith("80") or account_code.startswith("84"):
        return "Operating Expenses"
    return "Other Expenses"


async def generate_income_statement(
    db: AsyncSession,
    from_date: date,
    to_date: date,
) -> IncomeStatementResponse:

    if not can_view_income_statement():
        raise ValueError("Permission denied")

    result = await db.execute(
        select(Account).where(
            Account.account_type.in_(["INCOME", "EXPENSE"]),
            Account.is_posting.is_(True),
            Account.is_active.is_(True),
        )
    )
    accounts = result.scalars().all()

    sections = defaultdict(list)
    section_totals = defaultdict(lambda: Decimal("0.00"))

    for account in accounts:
        balance_query = (
            select(
                func.coalesce(func.sum(JournalLine.debit - JournalLine.credit), 0)
            )
            .join(JournalEntry)
            .where(
                JournalLine.account_id == account.id,
                JournalEntry.is_posted.is_(True),
                JournalEntry.entry_date.between(from_date, to_date),
            )
        )

        movement = Decimal((await db.execute(balance_query)).scalar())

        if movement == 0:
            continue

        if account.account_type == "INCOME":
            movement = movement * Decimal("-1")

        section_name = classify_section(account.code)

        sections[section_name].append(
            IncomeStatementRow(
                section=section_name,
                account_code=account.code,
                account_name=account.name,
                amount=movement,
            )
        )

        section_totals[section_name] += movement

    response_sections: List[IncomeStatementSection] = []
    net_profit = Decimal("0.00")

    for name, rows in sections.items():
        total = section_totals[name]
        response_sections.append(
            IncomeStatementSection(
                name=name,
                total=total,
                rows=rows,
            )
        )
        net_profit += total

    return IncomeStatementResponse(
        from_date=from_date,
        to_date=to_date,
        sections=response_sections,
        net_profit=net_profit,
    )


async def build_income_statement(db, from_date, to_date):
    ledger = await build_ledger(db, from_date, to_date)

    rows = []
    income_total = 0
    expense_total = 0

    for code, name, debit, credit, balance in ledger:
        if code.startswith("6"):
            amount = credit - debit
            if amount != 0:
                rows.append(["Income", code, name, amount])
                income_total += amount

        if code.startswith("7") or code.startswith("8"):
            amount = debit - credit
            if amount != 0:
                rows.append(["Expense", code, name, amount])
                expense_total += amount

    net_profit = income_total - expense_total
    rows.append(["", "", "Net Profit / Loss", net_profit])

    return rows