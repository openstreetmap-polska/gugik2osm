import datetime
import logging
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pyarrow as pa
import pyarrow.parquet as pq
from airflow import DAG, AirflowException
from airflow.models import Variable, TaskInstance
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from utils.discord import send_dag_run_status
from utils.osm.changesets import parse_full_changeset_file
from utils.parquet import changeset_schema

logger = logging.getLogger()

send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)

s3_bucket_name = "tt-osm-changesets"
temp_dir = Path("/opt/gugik2osm/temp_changesets/")
temp_parquet_dir = temp_dir / "parquet"
temp_file_name = temp_dir / "changesets-latest.osm.bz2"
file_url = "https://planet.osm.org/planet/changesets-latest.osm.bz2"


def save_parquet(data: List[dict], file_path: str) -> None:
    table = pa.Table.from_pylist(data, changeset_schema)
    logger.info(f"Converted changesets to PyArrow Table with: {table.num_rows} rows.")
    pq.write_table(table, file_path)
    logger.info(f"Parquet file saved successfully to: {file_path}")


def process_changesets(**kwargs) -> None:
    hook = S3Hook(aws_conn_id="aws_tt_s3")
    logger.info(f"Processing file: {temp_file_name.as_posix()}")
    paths_to_upload = []
    data = []
    currently_processed_year = 2005  # first changesets in the files are from 2005
    for changeset in parse_full_changeset_file(temp_file_name):
        if not changeset.open:
            changeset_year = changeset.closed_at.year
            if changeset_year != currently_processed_year:
                key = f"closed_year={changeset_year}/{changeset_year}.parquet"
                path = temp_parquet_dir / f"{changeset_year}.parquet"
                save_parquet(data, path.as_posix())
                paths_to_upload.append((path, key))
                logger.info(f"Uploading file: {path} to: s3://{s3_bucket_name}/{key}")
                hook.load_file(
                    filename=path,
                    bucket_name=s3_bucket_name,
                    key=f"full/{key}",
                    replace=True,
                )
                logger.info("Upload finished.")
                data = [changeset.transform_to_dict()]
            else:
                data.append(changeset.transform_to_dict())

        ti: TaskInstance = kwargs["ti"]
        processed_datetime = ti.start_date
        hook.load_string(
            string_data=processed_datetime.isoformat(),
            bucket_name=s3_bucket_name,
            key="full/dag_run_date.txt",
            replace=True,
        )
        logger.info("Files uploaded to s3 successfully.")


with DAG(
    dag_id="changesets_full_hist_file_to_parquet",
    description="Downloads changeset full history files and converts them to parquet.",
    start_date=datetime.datetime(2022, 11, 27),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    # on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    download_xml_file_task = BashOperator(
        task_id="download_xml_file",
        bash_command=f"""
            wget --quiet -O {temp_file_name.as_posix()} {file_url}
        """.strip(),
    )

    process_changesets_task = PythonOperator(
        task_id="process_changesets",
        python_callable=process_changesets,
    )

    delete_local_parquet_files = BashOperator(
        task_id="delete_parquet_files",
        bash_command=f"""
            rm -r {temp_parquet_dir.as_posix()}/*
        """
    )

    delete_xml_file_task = BashOperator(
        task_id="delete_xml_file",
        bash_command=f"""
            rm {temp_file_name.as_posix()}
        """.strip(),
    )

    chain(
        download_xml_file_task,
        process_changesets_task,
        delete_xml_file_task,
    )
