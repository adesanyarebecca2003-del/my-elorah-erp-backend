from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory_fifo_layer import InventoryFIFOLayer


async def consume_fifo_layers(
    db: AsyncSession,
    product_id,
    quantity: int,
) -> Decimal:
    """
    Consume FIFO layers using quantity_in / quantity_out.
    Returns total cost (COGS).
    """

    qty_needed = int(quantity)
    if qty_needed <= 0:
        raise ValueError("Quantity must be greater than zero")

    result = await db.execute(
        select(InventoryFIFOLayer)
        .where(
            InventoryFIFOLayer.product_id == product_id,
            InventoryFIFOLayer.quantity_in > InventoryFIFOLayer.quantity_out,
        )
        .order_by(InventoryFIFOLayer.received_date.asc())
        .with_for_update()
    )

    layers = result.scalars().all()

    total_cost = Decimal("0.00")

    for layer in layers:
        if qty_needed <= 0:
            break

        available = int(layer.quantity_in) - int(layer.quantity_out)
        if available <= 0:
            continue

        consume_qty = min(available, qty_needed)

        layer.quantity_out = int(layer.quantity_out) + int(consume_qty)
        total_cost += Decimal(consume_qty) * Decimal(layer.unit_cost)

        qty_needed -= int(consume_qty)

    if qty_needed > 0:
        raise ValueError("Insufficient inventory for FIFO consumption")

    return total_cost