import datetime
from functools import partial

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import ShortCircuitOperator, PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models.baseoperator import chain

from utils.discord import send_dag_run_status
from utils.expired_tiles import insert_tiles_from_n_newest_files
from utils.process_locks import (
    no_prg_updates_in_progress,
    set_process_status_running,
    set_process_status_finished,
    PROCESS_NAMES,
    STATUSES,
)

process_name = PROCESS_NAMES.incremental_update
mark_process_as_running = partial(set_process_status_running, process_name)
mark_process_as_failed = partial(set_process_status_finished, process_name, STATUSES.fail)
mark_process_as_succeeded = partial(set_process_status_finished, process_name, STATUSES.success)
send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=True)


default_args = {
    "retries": 1,
    "retry_delay": datetime.timedelta(seconds=10),
    "depends_on_past": False,
    "email": [],
    "email_on_failure": False,
    "email_on_retry": False,
}


with DAG(
    dag_id="data_update_incremental",
    description="Updates data every minute",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="*/1 * * * *",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
    max_active_runs=1,
    default_args=default_args,
) as dag:

    insert_expired_tiles_task = PythonOperator(
        task_id="insert_expired_tiles",
        python_callable=insert_tiles_from_n_newest_files,
        op_args=["/opt/gugik2osm/imposm3/exptiles/"],
    )

    check_process_locks_task = ShortCircuitOperator(
        task_id="check_if_update_in_progress",
        python_callable=no_prg_updates_in_progress,
    )

    set_process_lock_task = PythonOperator(
        task_id="mark_process_as_running",
        python_callable=mark_process_as_running,
    )

    process_excluded_queue_task = PostgresOperator(
        task_id="process_excluded_queue",
        sql="call process_excluded_queue()",
        autocommit=True,
        on_failure_callback=mark_process_as_failed,
    )

    run_partial_update_task = PostgresOperator(
        task_id="run_incremental_update",
        sql="call partial_update()",
        autocommit=True,
        on_failure_callback=mark_process_as_failed,
    )

    release_process_lock_task = PythonOperator(
        task_id="mark_process_as_succeeded",
        python_callable=mark_process_as_succeeded,
        on_failure_callback=mark_process_as_failed,
    )

    # set task execution order
    chain(
        insert_expired_tiles_task,
        check_process_locks_task,
        set_process_lock_task,
        process_excluded_queue_task,
        run_partial_update_task,
        release_process_lock_task,
    )
