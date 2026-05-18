import streamlit as st
import pandas as pd
import sqlalchemy

st.set_page_config(page_title="F&B Data Warehouse", layout="wide")
st.title("🍽️ F&B Operations Dashboard")
st.caption("Live data from PostgreSQL mart tables via dbt pipeline")

DB_URL = "postgresql://postgres:fbpassword@localhost:5433/fb_warehouse"
engine = sqlalchemy.create_engine(DB_URL)

# ── Load data ─────────────────────────────────────────────────────────────────
revenue   = pd.read_sql("SELECT * FROM mart_revenue ORDER BY order_date", engine)
inventory = pd.read_sql("SELECT * FROM mart_inventory_health ORDER BY days_cover_remaining", engine)
cogs      = pd.read_sql("SELECT * FROM mart_cogs_margin ORDER BY gross_margin_pct DESC", engine)

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.subheader("Weekly KPIs")
col1, col2, col3, col4 = st.columns(4)
last7 = revenue[revenue["order_date"] >= revenue["order_date"].max() - pd.Timedelta(days=7)]
col1.metric("Revenue (7d)",    f"£{last7['daily_revenue_gbp'].sum():,.0f}")
col2.metric("Orders (7d)",     f"{last7['order_count'].sum():,}")
col3.metric("Avg Order Value", f"£{last7['avg_order_value'].mean():.2f}")
col4.metric("Items Need Reorder", f"{(inventory['needs_reorder']=='yes').sum()}")

st.divider()

# ── Revenue chart ─────────────────────────────────────────────────────────────
st.subheader("Daily Revenue by Outlet")
pivot = revenue.pivot_table(
    index="order_date", columns="outlet_id",
    values="daily_revenue_gbp", aggfunc="sum"
)
st.line_chart(pivot)

st.divider()

# ── Two columns ───────────────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Gross Margin by SKU")
    st.bar_chart(cogs.set_index("item_sku")["gross_margin_pct"])

with right:
    st.subheader("Inventory Health")
    st.dataframe(
        inventory[["outlet_id","item_sku","stock_on_hand","days_cover_remaining","needs_reorder"]],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ── COGS detail ───────────────────────────────────────────────────────────────
st.subheader("COGS & Margin Detail")
st.dataframe(
    cogs.style.format({
        "total_revenue_gbp": "£{:,.2f}",
        "total_cost_gbp":    "£{:,.2f}",
        "gross_profit_gbp":  "£{:,.2f}",
        "gross_margin_pct":  "{:.1f}%",
    }),
    use_container_width=True,
    hide_index=True
)
