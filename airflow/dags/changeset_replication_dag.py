import datetime
import logging
from functools import partial
from pathlib import Path

from airflow import DAG, AirflowException
from airflow.models import Variable, TaskInstance
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator, ShortCircuitOperator
import pyarrow as pa
import pyarrow.parquet as pq

from utils.osm.changesets import find_newest_changeset_replication_sequence, changesets_between_sequences
from utils.parquet import changeset_schema
from utils.discord import send_dag_run_status


logger = logging.getLogger()

send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)

last_processed_sequence_variable_name = "last_processed_changeset_sequence"
date_base_dir = Path("/var/www/data/changesets/replication/")


def check_if_anything_to_run(**kwargs) -> bool:
    last_processed: str = Variable.get(last_processed_sequence_variable_name)
    if last_processed is None:
        raise AirflowException(f"Variable: {last_processed_sequence_variable_name} does not exist.")
    newest = find_newest_changeset_replication_sequence()
    return newest.formatted > last_processed


def process_changesets(**kwargs) -> None:
    last_processed: str = Variable.get(last_processed_sequence_variable_name, "")
    newest = find_newest_changeset_replication_sequence()
    logger.info(f"Processing files from: {last_processed} to: {newest.formatted}")
    changesets = changesets_between_sequences(last_processed, newest.number)
    data = [changeset.transform_to_dict() for changeset in changesets]
    table = pa.Table.from_pylist(data, changeset_schema)
    logger.info(f"Converted changesets to PyArrow Table with: {table.num_rows} rows.")
    ti: TaskInstance = kwargs["ti"]
    processed_datetime = ti.start_date
    relative_path = f"{processed_datetime.date().isoformat()}/{processed_datetime.isoformat()}.parquet"
    logger.info(f"Saving to file name: {relative_path}")
    file_path = date_base_dir / relative_path
    file_path.parent.mkdir(exist_ok=True)  # make sure dir exists
    pq.write_table(table, file_path.as_posix())
    logger.info("File saved successfully.")
    Variable.set(last_processed_sequence_variable_name, newest.formatted)
    logger.info(f"Variable: {last_processed_sequence_variable_name} set to: {newest.formatted}")


with DAG(
    dag_id="changesets_replication_to_parquet",
    description="Downloads changeset replication files and converts them to parquet.",
    start_date=datetime.datetime(2022, 11, 25),
    schedule_interval=datetime.timedelta(minutes=1),
    catchup=False,
    max_active_runs=1,
    # on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    check_if_anything_to_process_task = ShortCircuitOperator(
        task_id="check_if_anything_to_process",
        python_callable=check_if_anything_to_run,
    )

    process_changesets_task = PythonOperator(
        task_id="process_changesets",
        python_callable=process_changesets,
    )

    chain(
        check_if_anything_to_process_task,
        process_changesets_task,
    )
