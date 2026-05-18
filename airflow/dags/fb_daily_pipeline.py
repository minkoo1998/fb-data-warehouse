from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import subprocess, sys, os

default_args = {
    "owner": "mayank",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_extractor(script_name):
    project_dir = "/opt/airflow/project"
    result = subprocess.run(
        [sys.executable, f"{project_dir}/ingestion/{script_name}"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(result.stderr)

with DAG(
    dag_id="fb_daily_pipeline",
    schedule_interval="0 6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["fb", "production"],
    description="Daily F&B ELT: extract → bronze → dbt → marts",
) as dag:

    ingest_pos = PythonOperator(
        task_id="ingest_pos_sales",
        python_callable=run_extractor,
        op_args=["pos_extractor.py"],
    )

    ingest_supplier = PythonOperator(
        task_id="ingest_supplier_invoices",
        python_callable=run_extractor,
        op_args=["supplier_extractor.py"],
    )

    ingest_inventory = PythonOperator(
        task_id="ingest_inventory",
        python_callable=run_extractor,
        op_args=["inventory_extractor.py"],
    )

    run_dbt = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd /opt/airflow/project/dbt_fb && dbt run --profiles-dir /opt/airflow/project/dbt_fb && dbt test --profiles-dir /opt/airflow/project/dbt_fb",
    )

    # 3 ingest tasks run in parallel, then dbt runs
    [ingest_pos, ingest_supplier, ingest_inventory] >> run_dbt
