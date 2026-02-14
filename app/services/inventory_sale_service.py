from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    InventorySale,
    InventorySaleLine,
    InventoryProduct,
    Account,
)
from app.services.journal_service import create_journal_draft
from app.schemas.journal_entry import JournalEntryCreate, JournalLineCreate
from app.services.period_guard import ensure_period_open
from app.services.inventory_fifo_service import consume_fifo_layers


async def create_inventory_sale(db: AsyncSession, payload):
    # 1) Period check
    await ensure_period_open(db, payload.sale_date)

    # 2) Load products WITH category
    product_ids = {line.product_id for line in payload.lines}

    result = await db.execute(
        select(InventoryProduct)
        .where(InventoryProduct.id.in_(product_ids))
        .options(selectinload(InventoryProduct.category))
    )
    products = {p.id: p for p in result.scalars().all()}

    if len(products) != len(product_ids):
        raise ValueError("Invalid product in sale")

    # 3) Create sale header
    sale = InventorySale(
        sale_date=payload.sale_date,
        customer=payload.customer,
    )
    db.add(sale)
    await db.flush()

    journal_lines: list[JournalLineCreate] = []

    total_revenue = Decimal("0.00")
    revenue_by_account: dict[str, Decimal] = {}

    # amount_received is per sale transaction
    amount_received = Decimal(getattr(payload, "amount_received", Decimal("0.00")) or Decimal("0.00"))

    # 4) Process each sale line
    for line in payload.lines:
        product = products[line.product_id]
        category = product.category

        if not category:
            raise ValueError("Product has no category")

        qty = int(Decimal(line.quantity))
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero")

        unit_price = Decimal(line.unit_price)
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")

        # Create sale line
        sale_line = InventorySaleLine(
            sale_id=sale.id,
            product_id=product.id,
            quantity=qty,
            unit_price=unit_price,
        )
        db.add(sale_line)
        await db.flush()

        # Revenue for this line
        revenue = Decimal(qty) * unit_price
        total_revenue += revenue

        # --- FIFO CONSUMPTION (COGS) ---
        total_cost = await consume_fifo_layers(db, product.id, qty)
        sale_line.fifo_cost = total_cost

        # Fetch account codes (JournalLineCreate requires account_code)
        cogs_acc = await db.get(Account, category.cogs_account_id)
        inv_acc = await db.get(Account, category.inventory_account_id)
        rev_acc = await db.get(Account, category.revenue_account_id)

        if not cogs_acc or not inv_acc or not rev_acc:
            raise ValueError("Category accounts not properly linked (COGS/Inventory/Revenue)")

        # DR COGS
        journal_lines.append(
            JournalLineCreate(
                account_code=cogs_acc.code,
                debit=total_cost,
                credit=Decimal("0.00"),
            )
        )

        # CR Inventory
        journal_lines.append(
            JournalLineCreate(
                account_code=inv_acc.code,
                debit=Decimal("0.00"),
                credit=total_cost,
            )
        )

        # Collect revenue by revenue account (supports multiple categories)
        revenue_by_account[rev_acc.code] = revenue_by_account.get(rev_acc.code, Decimal("0.00")) + revenue

    # ==============================
    # PAYMENT / RECEIVABLE SPLIT
    # ==============================
    if amount_received > total_revenue:
        raise ValueError("Amount received cannot exceed total sale amount")

    # DR Bank/Cash (1010)
    if amount_received > 0:
        journal_lines.append(
            JournalLineCreate(
                account_code="1010",
                debit=amount_received,
                credit=Decimal("0.00"),
            )
        )

    # DR Trade Receivable (1110) for outstanding
    balance = total_revenue - amount_received
    if balance > 0:
        journal_lines.append(
            JournalLineCreate(
                account_code="1110",
                debit=balance,
                credit=Decimal("0.00"),
            )
        )

    # CR Revenue (grouped by revenue account)
    for acc_code, amt in revenue_by_account.items():
        if amt > 0:
            journal_lines.append(
                JournalLineCreate(
                    account_code=acc_code,
                    debit=Decimal("0.00"),
                    credit=amt,
                )
            )

    # 5) Create journal draft
    journal = await create_journal_draft(
        db,
        JournalEntryCreate(
            entry_date=payload.sale_date,
            description=f"Inventory Sale {sale.id}",
            lines=journal_lines,
        ),
    )

    # 6) Link journal
    sale.journal_entry_id = journal.id

    await db.commit()
    await db.refresh(sale)
    return sale