FROM apache/airflow:2.11.2
USER airflow
# Airflow 2.11 constrains SQLAlchemy to 1.4; keep OncoVerse's SQLAlchemy 2
# and model dependencies in an isolated venv used by the DAG's BashOperator.
COPY orchestration/airflow/requirements-airflow.txt /tmp/oncoverse-requirements.txt
RUN python -m venv /home/airflow/oncoverse-venv \
    && /home/airflow/oncoverse-venv/bin/pip install --no-cache-dir -r /tmp/oncoverse-requirements.txt
