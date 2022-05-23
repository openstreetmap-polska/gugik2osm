import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import delete
from airflow.models import DAG, Log, DagRun, TaskInstance, TaskReschedule, Variable
from airflow.jobs.base_job import BaseJob
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.utils.state import State
from airflow.utils.session import provide_session

EXPIRATION_WEEKS = 3


@provide_session
def delete_old_database_entries_by_model(table, date_col, session=None):
    expiration_date = datetime.now(timezone.utc) - timedelta(weeks=EXPIRATION_WEEKS)
    query = delete(table).where(date_col < expiration_date)

    if "state" in dir(table):
        query = query.where(State.RUNNING != "state")

    result = session.execute(query)
    logging.info(
        "Deleted %s rows from the database for the %s table that are older than %s.",
        result.rowcount,
        table,
        expiration_date,
    )


def delete_old_database_entries():

    if Variable.get("ENABLE_DB_TRUNCATION", "") != "True":
        logging.warning("This DAG will delete all data older than %s weeks.", EXPIRATION_WEEKS)
        logging.warning("To enable this, create an Airflow Variable called ENABLE_DB_TRUNCATION set to 'True'")
        logging.warning("Skipping truncation until explicitly enabled.")
        return

    delete_old_database_entries_by_model(TaskInstance, TaskInstance.end_date)
    delete_old_database_entries_by_model(DagRun, DagRun.end_date)
    delete_old_database_entries_by_model(BaseJob, BaseJob.end_date)
    delete_old_database_entries_by_model(Log, Log.dttm)
    delete_old_database_entries_by_model(TaskReschedule, TaskReschedule.end_date)


dag = DAG(
    "airflow-utils.truncate-database",
    start_date=days_ago(1),
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=20),
    schedule_interval="@daily",
    catchup=False,
)

PythonOperator(
    task_id="cleanup-old-database-entries",
    dag=dag,
    python_callable=delete_old_database_entries,
)
