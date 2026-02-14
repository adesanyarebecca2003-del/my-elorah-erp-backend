import csv
from io import StringIO


def export_inventory_valuation_csv(valuation: dict):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
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
            writer.writerow([
                category["category_code"],
                category["category_name"],
                product["sku"],
                product["name"],
                float(product["quantity"]),
                float(product["unit_cost_avg"]),
                float(product["value"])
            ])

    output.seek(0)
    return output