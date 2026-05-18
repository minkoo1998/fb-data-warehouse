import pandas as pd
import boto3
import io
import os
from datetime import date
 
# ── Config ────────────────────────────────────────────────────────────────────
BUCKET    = "fb-dw"
S3_PREFIX = "bronze/inventory"
 
REQUIRED_COLUMNS = [
    "record_id", "outlet_id", "item_sku",
    "stock_on_hand", "reorder_threshold", "needs_reorder",
    "unit_cost_gbp", "last_updated", "supplier_name",
]
 
# ── Helpers ───────────────────────────────────────────────────────────────────
def validate_schema(df: pd.DataFrame) -> None:
    """Raise if any required column is missing."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Inventory Excel missing columns: {missing}")
 
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning before upload."""
    df = df.copy()
    df.columns          = [c.strip().lower() for c in df.columns]
    df["outlet_id"]     = df["outlet_id"].str.strip()
    df["item_sku"]      = df["item_sku"].str.strip().str.upper()
    df["needs_reorder"] = df["needs_reorder"].str.strip().str.lower()
    df["supplier_name"] = df["supplier_name"].str.strip()
    df["last_updated"]  = pd.to_datetime(df["last_updated"]).dt.strftime("%Y-%m-%d %H:%M:%S")
 
    # Enforce numeric types — catches any stray strings
    df["stock_on_hand"]     = pd.to_numeric(df["stock_on_hand"], errors="coerce").fillna(0).astype(int)
    df["reorder_threshold"] = pd.to_numeric(df["reorder_threshold"], errors="coerce").fillna(0).astype(int)
    df["unit_cost_gbp"]     = pd.to_numeric(df["unit_cost_gbp"], errors="coerce").round(2)
 
    df = df.dropna(subset=["record_id"])
    df = df.drop_duplicates(subset=["outlet_id", "item_sku"])     # one row per outlet+sku
    return df
 
def upload_to_s3(df: pd.DataFrame, bucket: str, key: str) -> None:
    """Upload dataframe as CSV to S3."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())
 
# ── Main extractor ────────────────────────────────────────────────────────────
def extract_inventory(source_path: str, bucket: str = BUCKET) -> None:
    print(f"[inventory_extractor] Reading: {source_path}")
 
    # 1. Read Excel (openpyxl engine handles .xlsx)
    df = pd.read_excel(source_path, sheet_name="Inventory", engine="openpyxl")
    print(f"  Raw rows loaded : {len(df):,}")
 
    # 2. Validate schema
    validate_schema(df)
    print(f"  Schema OK       : {list(df.columns)}")
 
    # 3. Clean
    df = clean(df)
    print(f"  Rows after clean: {len(df):,}")
 
    # 4. Upload to S3 bronze layer, partitioned by today's date
    today   = date.today().isoformat()
    s3_key  = f"{S3_PREFIX}/{today}/inventory.csv"
 
    # ── Local fallback (no AWS creds) ─────────────────────────────────────────
    local_out = f"bronze/inventory/{today}"
    os.makedirs(local_out, exist_ok=True)
    local_path = f"{local_out}/inventory.csv"
    df.to_csv(local_path, index=False)
    print(f"  ✓ Saved locally : {local_path}")
 
    # Comment the block above and uncomment below once AWS is configured:
    # upload_to_s3(df, bucket, s3_key)
    # print(f"  ✓ Uploaded to S3: s3://{bucket}/{s3_key}")
 
    # 5. Summary stats
    print(f"\n  --- Summary ---")
    print(f"  Total SKU-outlet records : {len(df)}")
    print(f"  Outlets                  : {sorted(df['outlet_id'].unique().tolist())}")
    print(f"  SKUs tracked             : {sorted(df['item_sku'].unique().tolist())}")
    print(f"  Items needing reorder    : {(df['needs_reorder'] == 'yes').sum()}")
    print(f"\n  Stock snapshot:")
    print(
        df[["outlet_id", "item_sku", "stock_on_hand", "needs_reorder"]]
        .sort_values(["outlet_id", "item_sku"])
        .to_string(index=False)
    )
 
if __name__ == "__main__":
    extract_inventory("data/inventory_sample.xlsx")