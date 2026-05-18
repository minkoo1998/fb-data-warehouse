import pandas as pd
import os
from datetime import date
from utils.schema_validator import validate_pos_schema

POS_SCHEMA = ["order_id", "outlet_id", "item_sku", "quantity", "unit_price", "order_ts"]

def extract_pos(source_path: str, bucket: str = "fb-dw") -> None:
    print(f"[pos_extractor] Reading: {source_path}")

    df = pd.read_csv(source_path)
    print(f"  Raw rows loaded : {len(df):,}")

    validate_pos_schema(df, POS_SCHEMA)
    print(f"  Schema OK       : {list(df.columns)}")

    df["order_ts"] = pd.to_datetime(df["order_ts"])
    df["order_date"] = df["order_ts"].dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["order_id"])
    df = df.drop_duplicates(subset=["order_id"])
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]
    df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)
    print(f"  Rows after clean: {len(df):,}")

    today = date.today().isoformat()
    local_out = f"bronze/pos/{today}"
    os.makedirs(local_out, exist_ok=True)
    local_path = f"{local_out}/pos_sales.csv"
    df.to_csv(local_path, index=False)
    print(f"  ✓ Saved locally : {local_path}")

    print(f"\n  --- Summary ---")
    print(f"  Total orders    : {len(df):,}")
    print(f"  Outlets         : {sorted(df['outlet_id'].unique().tolist())}")
    print(f"  SKUs            : {sorted(df['item_sku'].unique().tolist())}")
    print(f"  Revenue (£)     : £{df['line_total'].sum():,.2f}")
    print(f"  Date range      : {df['order_date'].min()} → {df['order_date'].max()}")

if __name__ == "__main__":
    extract_pos("data/pos_sales_sample.csv")
