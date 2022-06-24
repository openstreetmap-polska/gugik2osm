import datetime
from functools import partial

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator

from utils.process_locks import set_process_status_running, PROCESS_NAMES, set_process_status_finished, STATUSES
from utils.discord import send_dag_run_status
import utils.teryt as teryt


process_name = PROCESS_NAMES.teryt_update
mark_process_as_running = partial(set_process_status_running, process_name)
mark_process_as_failed = partial(set_process_status_finished, process_name, STATUSES.fail)
mark_process_as_succeeded = partial(set_process_status_finished, process_name, STATUSES.success)
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

    set_process_lock_task = PythonOperator(
        task_id="mark_process_as_running",
        python_callable=mark_process_as_running,
    )

    recreate_tables = PostgresOperator(
        task_id="recreate_tables",
        sql=teryt.sql_prepare_tables,
        postgres_conn_id=postgres_conn_id,
        autocommit=True,
        on_failure_callback=mark_process_as_failed,
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
            on_failure_callback=mark_process_as_failed,
        )
        for registry_name in teryt.registriesConfiguration.keys()
    ]

    release_process_lock_task = PythonOperator(
        task_id="mark_process_as_succeeded",
        python_callable=mark_process_as_succeeded,
        on_failure_callback=mark_process_as_failed,
    )

    chain(
        set_process_lock_task,
        recreate_tables,
        data_loading_tasks,
        release_process_lock_task,
    )
