from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    InventorySaleReturn,
    InventorySaleReturnLine,
    InventorySaleLine,
    InventoryFIFOLayer,
    InventoryProduct,
    Account,
)
from app.schemas.journal_entry import JournalEntryCreate, JournalLineCreate
from app.services.journal_service import create_journal_draft
from app.services.period_guard import ensure_period_open


async def create_inventory_sale_return(db: AsyncSession, payload):
    # 1) Period check
    await ensure_period_open(db, payload.return_date)

    # 2) Load sale lines + product + category
    sale_line_ids = {l.sale_line_id for l in payload.lines}

    result = await db.execute(
        select(InventorySaleLine)
        .where(InventorySaleLine.id.in_(sale_line_ids))
        .options(
            selectinload(InventorySaleLine.product).selectinload(InventoryProduct.category)
        )
    )
    sale_lines = {l.id: l for l in result.scalars().all()}

    if len(sale_lines) != len(sale_line_ids):
        raise ValueError("Invalid sale line")

    # 3) Create return header
    sale_return = InventorySaleReturn(
        return_date=payload.return_date,
        customer=payload.customer,
    )
    db.add(sale_return)
    await db.flush()

    journal_lines: list[JournalLineCreate] = []
    total_reversal = Decimal("0.00")

    # We'll group revenue reversal by revenue account code
    revenue_by_account: dict[str, Decimal] = {}

    # 4) Process each return line
    for line in payload.lines:
        sale_line = sale_lines[line.sale_line_id]

        if Decimal(line.quantity) > Decimal(sale_line.quantity):
            raise ValueError("Return quantity exceeds sold quantity")

        product = sale_line.product
        category = product.category

        if not category:
            raise ValueError("Product has no category")

        # Accounts -> JournalLineCreate needs account_code
        inv_acc = await db.get(Account, category.inventory_account_id)
        cogs_acc = await db.get(Account, category.cogs_account_id)
        rev_acc = await db.get(Account, category.revenue_account_id)

        if not inv_acc or not cogs_acc or not rev_acc:
            raise ValueError("Category accounts not properly linked (Inventory/COGS/Revenue)")

        if sale_line.fifo_cost is None:
            raise ValueError("Sale line missing fifo_cost (cannot compute return cost)")

        unit_cost = Decimal(sale_line.fifo_cost) / Decimal(sale_line.quantity)
        total_cost = unit_cost * Decimal(line.quantity)

        revenue_reversal = Decimal(sale_line.unit_price) * Decimal(line.quantity)
        total_reversal += revenue_reversal

        revenue_by_account[rev_acc.code] = revenue_by_account.get(rev_acc.code, Decimal("0.00")) + revenue_reversal

        # Restore inventory by creating a FIFO layer back in
        fifo_layer = InventoryFIFOLayer(
            product_id=product.id,
            purchase_line_id=None,  # IMPORTANT: FIFO purchase_line_id must allow NULL for returns
            received_date=payload.return_date,
            quantity_in=int(line.quantity),
            quantity_out=0,
            unit_cost=unit_cost,
        )
        db.add(fifo_layer)

        # Create return line record
        return_line = InventorySaleReturnLine(
            return_id=sale_return.id,
            sale_line_id=sale_line.id,
            quantity=int(line.quantity),
            fifo_reversal_cost=total_cost,
        )
        db.add(return_line)

        # DR Inventory
        journal_lines.append(
            JournalLineCreate(
                account_code=inv_acc.code,
                debit=total_cost,
                credit=Decimal("0.00"),
            )
        )

        # CR COGS (reverse expense)
        journal_lines.append(
            JournalLineCreate(
                account_code=cogs_acc.code,
                debit=Decimal("0.00"),
                credit=total_cost,
            )
        )

    # 5) Revenue reversal (DR Revenue)
    for acc_code, amt in revenue_by_account.items():
        if amt > 0:
            journal_lines.append(
                JournalLineCreate(
                    account_code=acc_code,
                    debit=amt,
                    credit=Decimal("0.00"),
                )
            )

    # 6) Refund split: amount_refunded vs remaining reduces receivable
    amount_refunded = Decimal(payload.amount_refunded or Decimal("0.00"))

    if amount_refunded > total_reversal:
        raise ValueError("Amount refunded cannot exceed total return value")

    # CR Bank/Cash (money goes out)
    if amount_refunded > 0:
        journal_lines.append(
            JournalLineCreate(
                account_code="1010",
                debit=Decimal("0.00"),
                credit=amount_refunded,
            )
        )

    # CR Trade Receivable (reduce what customer owes)
    balance = total_reversal - amount_refunded
    if balance > 0:
        journal_lines.append(
            JournalLineCreate(
                account_code="1110",
                debit=Decimal("0.00"),
                credit=balance,
            )
        )

    # 7) Create journal draft
    journal = await create_journal_draft(
        db,
        JournalEntryCreate(
            entry_date=payload.return_date,
            description=f"Inventory Sale Return {sale_return.id}",
            lines=journal_lines,
        ),
    )

    sale_return.journal_entry_id = journal.id

    await db.commit()
    await db.refresh(sale_return)
    return sale_return
