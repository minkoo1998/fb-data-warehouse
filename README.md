# 🍽️ F&B Data Warehouse

End-to-end data engineering project built on real-world F&B consulting experience. Ingests 10K+ daily records from 3 heterogeneous sources into a medallion architecture, transforms via dbt, orchestrated by Airflow, and served through a live Streamlit dashboard.

## Tech Stack
| Layer | Tools |
|---|---|
| Ingestion | Python, Pandas, boto3 |
| Storage | Local Bronze/Silver/Gold (S3-ready), PostgreSQL |
| Transformation | dbt Core — 8 models, 13 tests |
| Orchestration | Apache Airflow |
| Dashboard | Streamlit, Plotly |
| Infrastructure | Docker |

## Key Metrics
- 10,000+ POS records processed daily across 3 outlets
- £236K total revenue modelled across 90-day window
- 81.1% gross margin on top SKU (PIZZA-02)
- 4 inventory items flagged for reorder automatically
- Pipeline runs end-to-end in under 5 minutes

## Setup
1. Clone the repo and activate venv
2. Run `python data/generate_data.py`
3. Start PostgreSQL via Docker on port 5433
4. Run `dbt seed && dbt run && dbt test` inside `dbt_fb/`
5. Run `streamlit run dashboard/streamlit_app.py`
6. Start Airflow via `docker compose up -d` inside `airflow/`