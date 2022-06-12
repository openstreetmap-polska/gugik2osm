import datetime
from functools import partial

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator

from utils.discord import send_dag_run_status
import utils.teryt as teryt


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)
postgres_conn_id = "postgres_default"
teryt_conn_id = "teryt_api_prod"

default_args = {
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=60),
    "depends_on_past": False,
    "email": [],
    "email_on_failure": False,
    "email_on_retry": False,
}


with DAG(
    dag_id="teryt_loader",
    description="Loads TERYT data to DB.",
    start_date=datetime.datetime(2022, 6, 12),
    schedule_interval="0 1 * * MON-FRI",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
    max_active_runs=1,
    default_args=default_args,
) as dag:

    recreate_tables = PostgresOperator(
        task_id="recreate_tables",
        sql=teryt.sql_prepare_tables,
        postgres_conn_id=postgres_conn_id,
        autocommit=True,
    )

    data_loading_tasks = [
        PythonOperator(
            task_id=f"load_{registry_name}",
            python_callable=teryt.get_data_from_api_and_load_to_db,
            op_args=[
                registry_name,
                "{{ ds }}",
                teryt_conn_id,
                postgres_conn_id,
            ],
        )
        for registry_name in teryt.registriesConfiguration.keys()
    ]

    recreate_tables >> data_loading_tasks
