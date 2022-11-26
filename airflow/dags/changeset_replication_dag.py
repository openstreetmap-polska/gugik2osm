import datetime
import logging
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

import pyarrow as pa
import pyarrow.parquet as pq
from airflow import DAG, AirflowException
from airflow.models import Variable, TaskInstance
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from utils.discord import send_dag_run_status
from utils.osm.changesets import find_newest_changeset_replication_sequence, changesets_between_sequences
from utils.parquet import changeset_schema

logger = logging.getLogger()

send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)

last_processed_sequence_variable_name = "last_processed_changeset_sequence"
s3_bucket_name = "tt-osm-changesets"


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
    date_str = processed_datetime.date().isoformat()
    file_name = processed_datetime.strftime("%Y%m%d%H%M%S")
    with TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        parquet_file_path = temp_dir / f"{file_name}.parquet"
        pq.write_table(table, parquet_file_path.as_posix())
        logger.info("Temp file saved successfully.")
        hook = S3Hook(aws_conn_id="aws_tt_s3")
        hook.load_file(
            filename=parquet_file_path,
            bucket_name=s3_bucket_name,
            key=f"replication/last.parquet",
            replace=True,
        )
        hook.load_file(
            filename=parquet_file_path,
            bucket_name=s3_bucket_name,
            key=f"replication/dag_run_date={date_str}/{file_name}.parquet",
        )
        hook.load_string(
            string_data=newest.formatted,
            bucket_name=s3_bucket_name,
            key="state.txt",
            replace=True,
        )
        logger.info("Files uploaded to s3 successfully.")
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
