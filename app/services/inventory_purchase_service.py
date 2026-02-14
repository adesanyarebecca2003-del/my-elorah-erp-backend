from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    InventoryPurchase,
    InventoryPurchaseLine,
    InventoryFIFOLayer,
    InventoryProduct,
    Account,
)
from app.services.journal_service import create_journal_draft
from app.schemas.journal_entry import JournalEntryCreate
from app.schemas.journal_line import JournalLineCreate
from app.services.period_guard import ensure_period_open


async def create_inventory_purchase(
    db: AsyncSession,
    payload,
):
    # 1. Period check
    await ensure_period_open(db, payload.purchase_date)

    # 2. Load products WITH category
    product_ids = {line.product_id for line in payload.lines}

    result = await db.execute(
        select(InventoryProduct)
        .where(InventoryProduct.id.in_(product_ids))
        .options(selectinload(InventoryProduct.category))
    )

    products = {p.id: p for p in result.scalars().all()}

    if len(products) != len(product_ids):
        raise ValueError("Invalid product in purchase")

    # 3. Create purchase header
    purchase = InventoryPurchase(
        purchase_date=payload.purchase_date,
        supplier=payload.supplier,
        amount_paid=payload.amount_paid,
    )
    db.add(purchase)
    await db.flush()

    journal_lines: list[JournalLineCreate] = []
    total_amount = Decimal("0.00")

    # 4. Process each purchase line
    for line in payload.lines:
        product = products[line.product_id]
        category = product.category

        if not category or not category.inventory_account_id:
            raise ValueError("Inventory category not properly linked")

        purchase_line = InventoryPurchaseLine(
            purchase_id=purchase.id,
            product_id=product.id,
            quantity=line.quantity,
            unit_cost=line.unit_cost,
        )
        db.add(purchase_line)
        await db.flush()

        fifo_layer = InventoryFIFOLayer(
            product_id=product.id,
            purchase_line_id=purchase_line.id,
            received_date=payload.purchase_date,
            quantity_in=line.quantity,
            quantity_out=0,
            unit_cost=line.unit_cost,
        )
        db.add(fifo_layer)

        amount = Decimal(line.quantity) * Decimal(line.unit_cost)
        total_amount += amount

        # Inventory DR
        inv_account = await db.get(Account, category.inventory_account_id)
        if not inv_account:
            raise ValueError("Inventory account not found")

        journal_lines.append(
            JournalLineCreate(
                account_code=inv_account.code,
                debit=amount,
                credit=Decimal("0.00"),
            )
        )

    # ==============================
    # PAYMENT & PAYABLES LOGIC
    # ==============================

    if payload.amount_paid > total_amount:
        raise ValueError("Amount paid cannot exceed total purchase amount")

    # Cash / Bank CR
    if payload.amount_paid > 0:
        journal_lines.append(
            JournalLineCreate(
                account_code="1010",  # Bank / Cash
                debit=Decimal("0.00"),
                credit=payload.amount_paid,
            )
        )

    # Accounts Payable CR
    balance = total_amount - payload.amount_paid
    if balance > 0:
        journal_lines.append(
            JournalLineCreate(
                account_code="3010",  # Trade Payables
                debit=Decimal("0.00"),
                credit=balance,
            )
        )

    # 5. Create journal (ALL lines present)
    journal = await create_journal_draft(
        db,
        JournalEntryCreate(
            entry_date=payload.purchase_date,
            description=f"Inventory Purchase {purchase.id}",
            lines=journal_lines,
        ),
    )

    # 6. Link & persist
    purchase.journal_entry_id = journal.id

    await db.commit()
    await db.refresh(purchase)

    return purchase