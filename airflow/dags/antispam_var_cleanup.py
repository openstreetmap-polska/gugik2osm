import datetime
from functools import partial

from airflow import DAG
from airflow.operators.python import PythonOperator

from utils.discord import reset_dag_antispam_old_stats
from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


with DAG(
    dag_id="antispam_variable_cleanup",
    description="Reset counters after one hour.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="@hourly",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    PythonOperator(
        task_id="reset_counters_that_have_old_timestamps",
        python_callable=reset_dag_antispam_old_stats,
    )
