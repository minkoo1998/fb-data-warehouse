from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
 
fake = Faker('en_GB')
np.random.seed(42)
random.seed(42)
 
OUTLETS   = ["Leeds-Central", "Bradford", "Harrogate"]
SKUS      = ["BURGER-01", "PIZZA-02", "WRAP-03", "DRINK-04", "SIDE-05"]
PRICES    = {"BURGER-01": 10.99, "PIZZA-02": 12.99, "WRAP-03": 7.99, "DRINK-04": 3.49, "SIDE-05": 3.99}
SUPPLIERS = ["FreshFarm Ltd", "Metro Foods UK", "Northern Wholesale", "GreenLeaf Supplies"]
SUP_SKUS  = {
    "BURGER-01": "FreshFarm Ltd",
    "PIZZA-02":  "Metro Foods UK",
    "WRAP-03":   "Northern Wholesale",
    "DRINK-04":  "Metro Foods UK",
    "SIDE-05":   "GreenLeaf Supplies",
}
 
# ── 1. POS SALES ─────────────────────────────────────────────────────────────
print("Generating POS sales...")
rows = []
for _ in range(10_000):
    sku = np.random.choice(SKUS)
    rows.append({
        "order_id":   fake.uuid4(),
        "outlet_id":  np.random.choice(OUTLETS),
        "item_sku":   sku,
        "quantity":   np.random.randint(1, 6),
        "unit_price": PRICES[sku],
        "order_ts":   fake.date_time_between(start_date="-90d", end_date="now"),
    })
pd.DataFrame(rows).to_csv("data/pos_sales_sample.csv", index=False)
print(f"  ✓ pos_sales_sample.csv  — {len(rows):,} rows")
 
 
# ── 2. SUPPLIER INVOICES ─────────────────────────────────────────────────────
print("Generating supplier invoices...")
invoices = []
start = datetime.now() - timedelta(days=90)
for day_offset in range(90):
    invoice_date = start + timedelta(days=day_offset)
    # each supplier delivers 2-4 times per week
    if invoice_date.weekday() in [0, 2, 4]:          # Mon, Wed, Fri
        for sku, supplier in SUP_SKUS.items():
            units = np.random.randint(20, 120)
            cost  = round(PRICES[sku] * np.random.uniform(0.40, 0.55), 2)
            invoices.append({
                "invoice_id":     fake.uuid4(),
                "supplier_name":  supplier,
                "item_sku":       sku,
                "units_received": units,
                "unit_cost_gbp":  cost,
                "total_cost_gbp": round(units * cost, 2),
                "invoice_date":   invoice_date.strftime("%Y-%m-%d"),
                "payment_status": np.random.choice(
                    ["paid", "pending", "overdue"],
                    p=[0.80, 0.15, 0.05]
                ),
            })
pd.DataFrame(invoices).to_csv("data/supplier_invoices_sample.csv", index=False)
print(f"  ✓ supplier_invoices_sample.csv  — {len(invoices):,} rows")
 
 
# ── 3. INVENTORY ─────────────────────────────────────────────────────────────
print("Generating inventory...")
inventory_rows = []
for outlet in OUTLETS:
    for sku in SKUS:
        stock      = np.random.randint(10, 200)
        reorder_at = np.random.randint(15, 40)
        inventory_rows.append({
            "record_id":          fake.uuid4(),
            "outlet_id":          outlet,
            "item_sku":           sku,
            "stock_on_hand":      stock,
            "reorder_threshold":  reorder_at,
            "needs_reorder":      "yes" if stock <= reorder_at else "no",
            "unit_cost_gbp":      round(PRICES[sku] * 0.45, 2),
            "last_updated":       fake.date_time_between(start_date="-7d", end_date="now"),
            "supplier_name":      SUP_SKUS[sku],
        })
df_inv = pd.DataFrame(inventory_rows)
df_inv.to_excel("data/inventory_sample.xlsx", index=False, sheet_name="Inventory")
print(f"  ✓ inventory_sample.xlsx  — {len(inventory_rows)} rows")
 
 
print("\nAll 3 files generated successfully in data/")
print(df_inv[["outlet_id","item_sku","stock_on_hand","needs_reorder"]].to_string(index=False))
 