from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory_fifo_layer import InventoryFIFOLayer
from app.models.inventory_product import InventoryProduct
from app.models.inventory_category import InventoryCategory


async def generate_inventory_valuation(db: AsyncSession, as_at: date):
    stmt = (
        select(InventoryFIFOLayer, InventoryProduct, InventoryCategory)
        .join(InventoryProduct, InventoryProduct.id == InventoryFIFOLayer.product_id)
        .join(InventoryCategory, InventoryCategory.id == InventoryProduct.category_id)
        .where(
            # only layers with stock remaining
            InventoryFIFOLayer.quantity_in > InventoryFIFOLayer.quantity_out,
            # as-at cutoff: FIFO layers received on/before date
            InventoryFIFOLayer.received_date <= as_at,
        )
        .order_by(
            InventoryCategory.code.asc(),
            InventoryProduct.sku.asc(),
            InventoryFIFOLayer.received_date.asc(),
        )
    )

    result = await db.execute(stmt)

    categories = {}
    total_inventory_value = Decimal("0.00")

    for layer, product, category in result.all():
        # compute remaining qty safely (no need for created_at or risky casting)
        remaining_qty = Decimal(str((layer.quantity_in or 0) - (layer.quantity_out or 0)))
        if remaining_qty <= 0:
            continue

        unit_cost = Decimal(str(layer.unit_cost))
        layer_value = remaining_qty * unit_cost

        total_inventory_value += layer_value

        if category.id not in categories:
            categories[category.id] = {
                "category_code": category.code,
                "category_name": category.name,
                "quantity": Decimal("0.00"),
                "value": Decimal("0.00"),
                "products": {},
            }

        cat = categories[category.id]
        cat["quantity"] += remaining_qty
        cat["value"] += layer_value

        if product.id not in cat["products"]:
            cat["products"][product.id] = {
                "sku": product.sku,
                "name": product.name,
                "quantity": Decimal("0.00"),
                "value": Decimal("0.00"),
            }

        prod = cat["products"][product.id]
        prod["quantity"] += remaining_qty
        prod["value"] += layer_value

    response_categories = []

    for cat in categories.values():
        products = []
        for prod in cat["products"].values():
            unit_cost_avg = (
                (prod["value"] / prod["quantity"])
                if prod["quantity"] > 0
                else Decimal("0.00")
            )

            products.append(
                {
                    "sku": prod["sku"],
                    "name": prod["name"],
                    "quantity": prod["quantity"],
                    "value": prod["value"],
                    "unit_cost_avg": unit_cost_avg,
                }
            )

        response_categories.append(
            {
                "category_code": cat["category_code"],
                "category_name": cat["category_name"],
                "quantity": cat["quantity"],
                "value": cat["value"],
                "products": products,
            }
        )

    return {
        "as_at": as_at,
        "categories": response_categories,
        "total_inventory_value": total_inventory_value,
    }