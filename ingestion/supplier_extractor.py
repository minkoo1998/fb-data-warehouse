import pandas as pd
import boto3
import io
import os
from datetime import date
 
# ── Config ────────────────────────────────────────────────────────────────────
BUCKET    = "fb-dw"
S3_PREFIX = "bronze/supplier_invoices"
 
REQUIRED_COLUMNS = [
    "invoice_id", "supplier_name", "item_sku",
    "units_received", "unit_cost_gbp", "total_cost_gbp",
    "invoice_date", "payment_status",
]
 
# ── Helpers ───────────────────────────────────────────────────────────────────
def validate_schema(df: pd.DataFrame) -> None:
    """Raise if any required column is missing."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Supplier CSV missing columns: {missing}")
 
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning before upload."""
    df = df.copy()
    df.columns       = [c.strip().lower() for c in df.columns]   # normalise headers
    df["invoice_date"] = pd.to_datetime(df["invoice_date"]).dt.strftime("%Y-%m-%d")
    df["supplier_name"] = df["supplier_name"].str.strip()
    df["item_sku"]      = df["item_sku"].str.strip().str.upper()
    df["payment_status"] = df["payment_status"].str.strip().str.lower()
    df = df.dropna(subset=["invoice_id"])                          # drop rows with no id
    df = df.drop_duplicates(subset=["invoice_id"])                 # deduplicate
    return df
 
def upload_to_s3(df: pd.DataFrame, bucket: str, key: str) -> None:
    """Upload dataframe as CSV to S3."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())
 
# ── Main extractor ────────────────────────────────────────────────────────────
def extract_supplier(source_path: str, bucket: str = BUCKET) -> None:
    print(f"[supplier_extractor] Reading: {source_path}")
 
    # 1. Read
    df = pd.read_csv(source_path)
    print(f"  Raw rows loaded : {len(df):,}")
 
    # 2. Validate schema
    validate_schema(df)
    print(f"  Schema OK       : {list(df.columns)}")
 
    # 3. Clean
    df = clean(df)
    print(f"  Rows after clean: {len(df):,}")
 
    # 4. Upload to S3 bronze layer, partitioned by today's date
    today   = date.today().isoformat()
    s3_key  = f"{S3_PREFIX}/{today}/supplier_invoices.csv"
 
    # ── Local fallback (no AWS creds) ─────────────────────────────────────────
    # When testing locally without AWS, save to a local bronze/ folder instead.
    local_out = f"bronze/supplier_invoices/{today}"
    os.makedirs(local_out, exist_ok=True)
    local_path = f"{local_out}/supplier_invoices.csv"
    df.to_csv(local_path, index=False)
    print(f"  ✓ Saved locally : {local_path}")
 
    # Comment the block above and uncomment below once AWS is configured:
    # upload_to_s3(df, bucket, s3_key)
    # print(f"  ✓ Uploaded to S3: s3://{bucket}/{s3_key}")
 
    # 5. Summary stats
    print(f"\n  --- Summary ---")
    print(f"  Total invoices  : {len(df):,}")
    print(f"  Suppliers       : {df['supplier_name'].nunique()}")
    print(f"  SKUs covered    : {df['item_sku'].nunique()}")
    print(f"  Date range      : {df['invoice_date'].min()} → {df['invoice_date'].max()}")
    print(f"  Total cost (£)  : £{df['total_cost_gbp'].sum():,.2f}")
    payment_counts = df["payment_status"].value_counts().to_dict()
    print(f"  Payment status  : {payment_counts}")
 
if __name__ == "__main__":
    extract_supplier("data/supplier_invoices_sample.csv")