from io import BytesIO
from openpyxl import Workbook


def export_inventory_valuation_excel(valuation: dict):
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Valuation"

    ws.append([
        "Category Code",
        "Category Name",
        "Product SKU",
        "Product Name",
        "Quantity",
        "Unit Cost (Avg)",
        "Value"
    ])

    for category in valuation["categories"]:
        for product in category["products"]:
            ws.append([
                category["category_code"],
                category["category_name"],
                product["sku"],
                product["name"],
                float(product["quantity"]),
                float(product["unit_cost_avg"]),
                float(product["value"])
            ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output