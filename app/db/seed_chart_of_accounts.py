import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.account import Account, AccountType, NormalBalance


ACCOUNTS = [
    # ===================== ASSETS =====================
    # CURRENT ASSETS
    ("1000", "Cash and Cash Equivalents", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("1010", "Cash on Hand", AccountType.ASSET, NormalBalance.DEBIT, "1000", True, True),
    ("1020", "Bank Account", AccountType.ASSET, NormalBalance.DEBIT, "1000", True, True),
    ("1030", "POS Settlement Account", AccountType.ASSET, NormalBalance.DEBIT, "1000", True, True),

    ("1100", "Trade and Other Receivables", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("1110", "Trade Receivables", AccountType.ASSET, NormalBalance.DEBIT, "1100", True, True),
    ("1120", "Other Receivables", AccountType.ASSET, NormalBalance.DEBIT, "1100", True, True),

    ("1200", "Inventory", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("1210", "Inventory – Human Hair", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1220", "Inventory – Attachments", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1230", "Inventory – Synthetic Hair", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1240", "Inventory – Fibre Hair", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1250", "Inventory – Hair Care Products", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1260", "Inventory – Hair Accessories", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1270", "Inventory – Perfumes", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),
    ("1280", "Inventory – Jewellery", AccountType.ASSET, NormalBalance.DEBIT, "1200", True, True),

    ("1300", "Prepayments and Supplies", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("1310", "Prepaid Rent", AccountType.ASSET, NormalBalance.DEBIT, "1300", True, True),
    ("1320", "Prepaid Utilities", AccountType.ASSET, NormalBalance.DEBIT, "1300", True, True),
    ("1330", "Office Supplies", AccountType.ASSET, NormalBalance.DEBIT, "1300", True, True),

    # NON-CURRENT ASSETS
    ("2000", "Property, Plant and Equipment", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("2010", "Furniture and Fittings", AccountType.ASSET, NormalBalance.DEBIT, "2000", True, True),
    ("2020", "Equipment and Machinery", AccountType.ASSET, NormalBalance.DEBIT, "2000", True, True),
    ("2030", "Vehicles", AccountType.ASSET, NormalBalance.DEBIT, "2000", True, True),
    ("2040", "Land and Building", AccountType.ASSET, NormalBalance.DEBIT, "2000", True, True),

    ("2100", "Right-of-Use Assets", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("2110", "Right-of-Use Asset – Shop", AccountType.ASSET, NormalBalance.DEBIT, "2100", True, True),
    ("2120", "Right-of-Use Asset – Vehicle", AccountType.ASSET, NormalBalance.DEBIT, "2100", True, True),

    ("2200", "Intangible Assets", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("2210", "Trademark", AccountType.ASSET, NormalBalance.DEBIT, "2200", True, True),

    ("2300", "Long-term Investments", AccountType.ASSET, NormalBalance.DEBIT, None, False, True),
    ("2310", "Long-term Investments Account", AccountType.ASSET, NormalBalance.DEBIT, "2300", True, True),

    # ===================== LIABILITIES =====================
    ("3000", "Trade and Other Payables", AccountType.LIABILITY, NormalBalance.CREDIT, None, False, True),
    ("3010", "Trade Payables", AccountType.LIABILITY, NormalBalance.CREDIT, "3000", True, True),
    ("3020", "Other Payables", AccountType.LIABILITY, NormalBalance.CREDIT, "3000", True, True),

    ("3100", "Accrued Expenses", AccountType.LIABILITY, NormalBalance.CREDIT, None, False, True),
    ("3110", "Accrued Expenses Payable", AccountType.LIABILITY, NormalBalance.CREDIT, "3100", True, True),
    ("3120", "Salaries Payable", AccountType.LIABILITY, NormalBalance.CREDIT, "3100", True, True),

    ("3200", "Taxes Payable", AccountType.LIABILITY, NormalBalance.CREDIT, None, False, True),
    ("3210", "VAT Payable", AccountType.LIABILITY, NormalBalance.CREDIT, "3200", True, True),
    ("3220", "PAYE Payable", AccountType.LIABILITY, NormalBalance.CREDIT, "3200", True, True),
    ("3230", "Withholding Tax Payable", AccountType.LIABILITY, NormalBalance.CREDIT, "3200", True, True),

    ("3300", "Current Portion of Long-term Obligations", AccountType.LIABILITY, NormalBalance.CREDIT, None, False, True),
    ("3310", "Current Portion of Lease Liability", AccountType.LIABILITY, NormalBalance.CREDIT, "3300", True, True),
    ("3320", "Current Portion of Loans", AccountType.LIABILITY, NormalBalance.CREDIT, "3300", True, True),

    ("4000", "Long-term Borrowings", AccountType.LIABILITY, NormalBalance.CREDIT, None, False, True),
    ("4010", "Long-term Loans", AccountType.LIABILITY, NormalBalance.CREDIT, "4000", True, True),

    ("4100", "Lease Liabilities", AccountType.LIABILITY, NormalBalance.CREDIT, None, False, True),
    ("4110", "Lease Liability – Shop", AccountType.LIABILITY, NormalBalance.CREDIT, "4100", True, True),
    ("4120", "Lease Liability – Vehicle", AccountType.LIABILITY, NormalBalance.CREDIT, "4100", True, True),

    # ===================== EQUITY =====================
    ("5000", "Owner’s Equity", AccountType.EQUITY, NormalBalance.CREDIT, None, False, True),
    ("5010", "Owner’s Capital", AccountType.EQUITY, NormalBalance.CREDIT, "5000", True, True),
    ("5020", "Owner’s Drawings", AccountType.EQUITY, NormalBalance.DEBIT, "5000", True, True),
    ("5030", "Retained Earnings", AccountType.EQUITY, NormalBalance.CREDIT, "5000", True, True),

    # ===================== INCOME =====================
    ("6000", "Sales Revenue", AccountType.INCOME, NormalBalance.CREDIT, None, False, True),
    ("6010", "Sales – Human Hair", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6020", "Sales – Attachments", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6030", "Sales – Synthetic Hair", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6040", "Sales – Fibre Hair", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6050", "Sales – Hair Care Products", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6060", "Sales – Hair Accessories", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6070", "Sales – Perfumes", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),
    ("6080", "Sales – Jewellery", AccountType.INCOME, NormalBalance.CREDIT, "6000", True, True),

    ("6100", "Sales Returns and Allowances", AccountType.INCOME, NormalBalance.DEBIT, None, False, True),
    ("6110", "Sales Returns – Human Hair", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6120", "Sales Returns – Attachments", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6130", "Sales Returns – Synthetic Hair", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6140", "Sales Returns – Fibre Hair", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6150", "Sales Returns – Hair Care Products", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6160", "Sales Returns – Hair Accessories", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6170", "Sales Returns – Perfumes", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),
    ("6180", "Sales Returns – Jewellery", AccountType.INCOME, NormalBalance.DEBIT, "6100", True, True),

    ("6200", "Other Income", AccountType.INCOME, NormalBalance.CREDIT, None, False, True),
    ("6210", "Discount Received", AccountType.INCOME, NormalBalance.CREDIT, "6200", True, True),
    ("6220", "Commission Received", AccountType.INCOME, NormalBalance.CREDIT, "6200", True, True),
    ("6230", "Bad Debt Recovered", AccountType.INCOME, NormalBalance.CREDIT, "6200", True, True),
    ("6290", "Other Income General", AccountType.INCOME, NormalBalance.CREDIT, "6200", True, True),

    ("6300", "Inventory Adjustment Gains", AccountType.INCOME, NormalBalance.CREDIT, None, False, True),

    # ===================== EXPENSES =====================
    ("7000", "Cost of Sales", AccountType.EXPENSE, NormalBalance.DEBIT, None, False, True),
    ("7010", "Cost of Sales – Human Hair", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7020", "Cost of Sales – Attachments", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7030", "Cost of Sales – Synthetic Hair", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7040", "Cost of Sales – Fibre Hair", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7050", "Cost of Sales – Hair Care Products", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7060", "Cost of Sales – Hair Accessories", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7070", "Cost of Sales – Perfumes", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),
    ("7080", "Cost of Sales – Jewellery", AccountType.EXPENSE, NormalBalance.DEBIT, "7000", True, True),

    ("8000", "Operating Expenses", AccountType.EXPENSE, NormalBalance.DEBIT, None, False, True),

    ("8400", "Depreciation Expense", AccountType.EXPENSE, NormalBalance.DEBIT, "8000", True, True),

    ("8500", "Inventory Adjustment Losses", AccountType.EXPENSE, NormalBalance.DEBIT, None, False, True),
]


async def seed():
    async with SessionLocal() as db:
        existing = await db.execute(select(Account))
        if existing.first():
            print("Chart of Accounts already seeded.")
            return

        code_to_id = {}

        for code, name, atype, nb, parent, posting, locked in ACCOUNTS:
            if parent is None:
                acc = Account(
                    code=code,
                    name=name,
                    account_type=atype,
                    normal_balance=nb,
                    is_posting=posting,
                    is_system_locked=locked,
                )
                db.add(acc)
                await db.flush()
                code_to_id[code] = acc.id

        for code, name, atype, nb, parent, posting, locked in ACCOUNTS:
            if parent is not None:
                acc = Account(
                    code=code,
                    name=name,
                    account_type=atype,
                    normal_balance=nb,
                    parent_id=code_to_id[parent],
                    is_posting=posting,
                    is_system_locked=locked,
                )
                db.add(acc)

        await db.commit()
        print("✅ Full Chart of Accounts seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())