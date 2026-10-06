"""Optional scheduled generate -> ingest -> train demo pipeline."""
from datetime import datetime
from pathlib import Path
from airflow import DAG
from airflow.operators.bash import BashOperator

ROOT=Path(__file__).resolve().parents[3]
with DAG("oncoverse_local_demo_pipeline",start_date=datetime(2026,1,1),schedule="@daily",catchup=False,tags=["oncoverse","academic-demo"]) as dag:
    ingest=BashOperator(task_id="ingest_configured_csv_or_synthetic_demo",bash_command=f"cd '{ROOT}' && if [ -n \"$ONCOVERSE_INPUT_CSV\" ]; then \"${{ONCOVERSE_PYTHON:-python}}\" -m oncoverse.cli ingest-mapped \"$ONCOVERSE_INPUT_CSV\" --mapping \"$ONCOVERSE_MAPPING_JSON\"; else python scripts/generate_demo_data.py && \"${{ONCOVERSE_PYTHON:-python}}\" -m oncoverse.cli ingest data/synthetic_cancer_records.csv; fi")
    train=BashOperator(task_id="train_demo_model",bash_command=f"cd '{ROOT}' && \"${{ONCOVERSE_PYTHON:-python}}\" -m oncoverse.cli train")
    ingest >> train
