import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.models.baseoperator import chain


with DAG(
    dag_id="file_cleanup",
    description="Remove old files.",
    start_date=datetime.datetime(2022, 5, 23),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    start_task = DummyOperator(task_id="start")
    end_task = DummyOperator(task_id="end")

    remove_old_imposm_files_task = BashOperator(
        task_id="remove_old_imposm_files",
        bash_command=r"""
            set -e;
            find /opt/gugik2osm/imposm3/imposm_diff/0* -mtime +7 -type f -print -delete;
            find /opt/gugik2osm/imposm3/imposm_diff/0* -empty -type d -delete;
        """,
    )

    remove_old_changesets_task = BashOperator(
        task_id="remove_old_changesets",
        bash_command=r"""
            set -e;
            find /opt/gugik2osm/temp_changesets/ -name "*.osm.gz" -mtime +1 -type f -print -delete;
            find /opt/gugik2osm/temp_changesets/ -empty -type d -delete;
        """,
    )

    truncate_gugik2osm_log_files_task = BashOperator(
        task_id="truncate_gugik2osm_log_files",
        bash_command=r"""
            set -e;
            truncate -s 20000000 /opt/gugik2osm/log/data_update.log;
            truncate -s 20000000 /opt/gugik2osm/log/osm_changesets.log;
        """,
    )

    remove_old_airflow_logs_task = BashOperator(
        task_id="remove_old_airflow_logs",
        bash_command=r"""
            set -e;
            find /opt/gugik2osm/airflow/logs/**/*.log -mtime +15 -type f -print -delete;
            find /opt/gugik2osm/airflow/logs/ -empty -type d -delete;
        """,
    )

    chain(
        start_task,
        [
            remove_old_imposm_files_task,
            remove_old_changesets_task,
            truncate_gugik2osm_log_files_task,
            remove_old_airflow_logs_task,
        ],
        end_task,
    )
