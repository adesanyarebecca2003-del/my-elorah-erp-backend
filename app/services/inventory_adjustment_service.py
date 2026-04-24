# app/services/inventory_adjustment_service.py
from decimal import Decimal
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    InventoryAdjustment,
    InventoryAdjustmentLine,
    InventoryProduct,
    InventoryFIFOLayer,
    InventoryPurchase,
    InventoryPurchaseLine,
)
from app.schemas.journal_entry import JournalEntryCreate, JournalLineCreate
from app.services.journal_service import create_journal_draft
from app.services.period_guard import ensure_period_open


async def _create_system_purchase_line_for_adjustment_increase(
    db: AsyncSession,
    adjustment_date: date,
    product_id,
    quantity: int,
    unit_cost: Decimal,
):
    """
    Creates a minimal 'system' purchase + line so FIFO layer can reference
    purchase_line_id without changing DB schema.
    """

    total_cost = Decimal(quantity) * Decimal(str(unit_cost))

    purchase = InventoryPurchase(
        purchase_date=adjustment_date,
        supplier="SYSTEM - INVENTORY ADJUSTMENT",
        freight_cost=Decimal("0.00"),
        amount_paid=Decimal("0.00"),  # system record, not an actual payment
    )
    db.add(purchase)
    await db.flush()

    pline = InventoryPurchaseLine(
        purchase_id=purchase.id,
        product_id=product_id,
        quantity=quantity,
        unit_cost=Decimal(str(unit_cost)),
    )
    db.add(pline)
    await db.flush()

    return pline


async def create_inventory_adjustment(db: AsyncSession, payload):
    await ensure_period_open(db, payload.adjustment_date)

    product_ids = {l.product_id for l in payload.lines}

    result = await db.execute(
        select(InventoryProduct)
        .where(InventoryProduct.id.in_(product_ids))
        .options(selectinload(InventoryProduct.category))
    )
    products = {p.id: p for p in result.scalars().all()}

    if len(products) != len(product_ids):
        raise ValueError("Invalid product")

    adjustment = InventoryAdjustment(
        adjustment_date=payload.adjustment_date,
        reason=payload.reason,
        adjustment_type=payload.adjustment_type,
    )
    db.add(adjustment)
    await db.flush()

    journal_lines: list[JournalLineCreate] = []

    for line in payload.lines:
        product = products[line.product_id]
        category = product.category

        qty = int(line.quantity)
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero")

        if payload.adjustment_type == "INCREASE":
            if line.unit_cost is None:
                raise ValueError("Unit cost required for increase")

            unit_cost = Decimal(str(line.unit_cost))
            total_cost = Decimal(qty) * unit_cost

            # Create a system purchase line so FIFO has valid purchase_line_id
            pline = await _create_system_purchase_line_for_adjustment_increase(
                db=db,
                adjustment_date=payload.adjustment_date,
                product_id=product.id,
                quantity=qty,
                unit_cost=unit_cost,
            )

            # FIFO layer using your real model columns
            fifo = InventoryFIFOLayer(
                product_id=product.id,
                purchase_line_id=pline.id,
                received_date=payload.adjustment_date,
                quantity_in=qty,
                quantity_out=0,
                unit_cost=unit_cost,
            )
            db.add(fifo)

            # Journal (Gain on adjustment for increase)
            journal_lines += [
                JournalLineCreate(
                    account_id=category.inventory_account_id,
                    debit=total_cost,
                    credit=Decimal("0.00"),
                ),
                JournalLineCreate(
                    account_id=category.adjustment_gain_account_id,
                    debit=Decimal("0.00"),
                    credit=total_cost,
                ),
            ]

            db.add(
                InventoryAdjustmentLine(
                    adjustment_id=adjustment.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_cost=unit_cost,
                    fifo_cost_used=None,
                )
            )

        else:  # DECREASE
            qty_to_consume = qty
            total_cost = Decimal("0.00")

            fifo_layers_res = await db.execute(
                select(InventoryFIFOLayer)
                .where(
                    InventoryFIFOLayer.product_id == product.id,
                    InventoryFIFOLayer.quantity_in > InventoryFIFOLayer.quantity_out,
                    InventoryFIFOLayer.received_date <= payload.adjustment_date,
                )
                .order_by(InventoryFIFOLayer.received_date.asc())
                .with_for_update()
            )

            for layer in fifo_layers_res.scalars().all():
                if qty_to_consume <= 0:
                    break

                available = int(layer.quantity_in) - int(layer.quantity_out or 0)
                if available <= 0:
                    continue

                consume = min(available, qty_to_consume)

                layer.quantity_out = int(layer.quantity_out or 0) + int(consume)
                total_cost += Decimal(consume) * Decimal(str(layer.unit_cost))

                qty_to_consume -= int(consume)

            if qty_to_consume > 0:
                raise ValueError("Insufficient stock for adjustment")

            # Journal (Loss on adjustment for decrease)
            journal_lines += [
                JournalLineCreate(
                    account_id=category.adjustment_loss_account_id,
                    debit=total_cost,
                    credit=Decimal("0.00"),
                ),
                JournalLineCreate(
                    account_id=category.inventory_account_id,
                    debit=Decimal("0.00"),
                    credit=total_cost,
                ),
            ]

            db.add(
                InventoryAdjustmentLine(
                    adjustment_id=adjustment.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_cost=None,
                    fifo_cost_used=total_cost,
                )
            )

    journal = await create_journal_draft(
        db,
        JournalEntryCreate(
            entry_date=payload.adjustment_date,
            description=f"Inventory Adjustment {adjustment.id}",
            lines=journal_lines,
        ),
    )

    # Only set if your model has this field (safe)
    if hasattr(adjustment, "journal_entry_id"):
        adjustment.journal_entry_id = journal.id

    await db.commit()
    await db.refresh(adjustment)
    return adjustment