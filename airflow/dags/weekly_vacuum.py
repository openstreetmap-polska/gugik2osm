import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator


with DAG(
    dag_id="postgresql_vacuum_analyze",
    description="Run VACUUM ANALYZE in PostgreSQL database.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="10 4 * * TUE",
    catchup=False,
) as dag:

    PostgresOperator(
        task_id="vacuum_analyze",
        sql="VACUUM ANALYZE",
        autocommit=True,
    )
