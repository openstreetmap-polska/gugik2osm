import datetime
from functools import partial
from pathlib import Path

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.python import PythonSensor

from utils.discord import send_dag_run_status
from utils.process_locks import (
    full_prg_update_in_progress, PROCESS_NAMES, set_process_status_running,
    set_process_status_finished, STATUSES,
)

process_name = PROCESS_NAMES.incremental_update
mark_process_as_running = partial(set_process_status_running, process_name)
mark_process_as_failed = partial(set_process_status_finished, process_name, STATUSES.fail)
mark_process_as_succeeded = partial(set_process_status_finished, process_name, STATUSES.success)
send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


def check_imposm_state(diff_folder: str) -> datetime.datetime:
    path = Path(diff_folder) / "last.state.txt"
    content = path.read_text(encoding="utf-8")
    first_line = content.split("\n")[0].strip().replace(r"\:", ":")
    timestamp = datetime.datetime.fromisoformat(first_line.split("=")[0])
    return timestamp


def imposm_state_lag(diff_folder: str) -> datetime.timedelta:
    imposm_state_ts = check_imposm_state(diff_folder)
    return abs(datetime.datetime.now() - imposm_state_ts)


with DAG(
    dag_id="imposm3_reimport_osm_data",
    description="Reimport OSM data with imposm3.",
    start_date=datetime.datetime(2022, 6, 14),
    schedule_interval=None,
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    full_update_sensor_task = PythonSensor(
        task_id="full_update_sensor",
        python_callable=lambda: not full_prg_update_in_progress(),
        timeout=datetime.timedelta(hours=24).total_seconds(),
        mode="reschedule",
        poke_interval=datetime.timedelta(hours=1).total_seconds(),
    )

    stop_imposm_service_task = BashOperator(
        task_id="stop_imposm_service",
        bash_command='''
            set -e;
            sudo service imposm stop;
        '''.strip()
    )

    download_pbf_task = BashOperator(
        task_id="download_pbf",
        bash_command='''
            set -e;
            cd /opt/gugik2osm/imposm3/ ;
            sudo -u ttaras wget https://download.geofabrik.de/europe/poland-latest.osm.pbf ;
        '''.strip()
    )

    imposm_run_import_task = BashOperator(
        task_id="run_import",
        bash_command='''
            set -e;
            sudo -u ttaras /opt/gugik2osm/imposm3/imposm-0.11.1-linux-x86-64/imposm import -config /opt/gugik2osm/imposm3/config.json -read /opt/gugik2osm/imposm3/poland-latest.osm.pbf -overwritecache -write -diff -deployproduction
        '''.strip()
    )

    start_imposm_service_task = BashOperator(
        task_id="start_imposm_service",
        bash_command='''
            set -e;
            sudo service imposm stop;
        '''.strip()
    )

    set_process_lock_task = PythonOperator(
        task_id="mark_process_as_running",
        python_callable=mark_process_as_running,
    )

    release_process_lock_task = PythonOperator(
        task_id="mark_process_as_succeeded",
        python_callable=mark_process_as_succeeded,
        on_failure_callback=mark_process_as_failed,
    )

    wait_for_imposm_to_catchup = PythonSensor(
        task_id="wait_for_imposm_to_catchup",
        python_callable=lambda x: imposm_state_lag(x) < datetime.timedelta(minutes=5),
        op_args=["/opt/gugik2osm/imposm3/imposm_diff/"],
        mode="reschedule",
        poke_interval=datetime.timedelta(minutes=2).total_seconds(),
        timeout=datetime.timedelta(hours=6).total_seconds(),
        on_failure_callback=mark_process_as_failed,
    )

    delete_pbf_task = BashOperator(
        task_id="delete_pbf",
        bash_command='''
            set -e;
            cd /opt/gugik2osm/imposm3/ ;
            sudo -u ttaras rm poland-latest.osm.pbf ;
        '''.strip()
    )

    drop_backup_schema_task = PostgresOperator(
        task_id="drop_backup_schema",
        sql="DROP SCHEMA IF EXISTS backup CASCADE",
        autocommit=True,
    )

chain(
    full_update_sensor_task,
    download_pbf_task,
    stop_imposm_service_task,
    set_process_lock_task,
    imposm_run_import_task,
    start_imposm_service_task,
    wait_for_imposm_to_catchup,
    release_process_lock_task,
    [
        delete_pbf_task,
        drop_backup_schema_task,
    ],
)
