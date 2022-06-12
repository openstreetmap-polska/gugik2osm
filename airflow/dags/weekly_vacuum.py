import datetime
from functools import partial

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


with DAG(
    dag_id="postgresql_vacuum_analyze",
    description="Run VACUUM ANALYZE in PostgreSQL database.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="10 4 * * TUE",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    PostgresOperator(
        task_id="vacuum_analyze",
        sql="VACUUM ANALYZE",
        autocommit=True,
    )
