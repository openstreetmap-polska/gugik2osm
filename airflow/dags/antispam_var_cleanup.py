import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from utils.discord import reset_dag_antispam_old_stats

with DAG(
    dag_id="antispam_variable_cleanup",
    description="Reset counters after one hour.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="@hourly",
    catchup=False,
) as dag:

    pg_check_version_task = PythonOperator(
        task_id="reset_counters_that_have_old_timestamps",
        python_callable=reset_dag_antispam_old_stats,
    )
