import csv
import datetime
import logging
import os
from functools import partial
from pathlib import Path
from typing import List, Union

import pyarrow
import pyarrow.csv
import pyarrow.parquet
from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from utils.discord import send_dag_run_status
from utils.osm.changesets import parse_full_changeset_file
from utils.parquet import changeset_schema

logger = logging.getLogger()

send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)

s3_bucket_name = "tt-osm-changesets"
temp_dir = Path("/opt/gugik2osm/temp_changesets/")
temp_parquet_dir = temp_dir / "parquet"
temp_csv_dir = temp_dir / "csv"
temp_file_name = temp_dir / "changesets-latest.osm.bz2"
file_url = "https://planet.osm.org/planet/changesets-latest.osm.bz2"


def list_files(directory: Union[Path, str], extension: str) -> List[Path]:
    dir_contents: List[str] = os.listdir(directory)
    return [directory / Path(file) for file in dir_contents if file.endswith(extension)]


def convert_csv_to_parquet(csv_dir: Path, parquet_dir: Path) -> None:
    csv_files = list_files(csv_dir, "csv")
    def invalid_row_handler(row: pyarrow.csv.InvalidRow) -> str:
        logger.warning(f"row could not be parsed: {row}")
        return "skip"
    for csv_file in csv_files:
        csv_path = csv_file.as_posix()
        parquet_path = parquet_dir / csv_file.name.replace("csv", "parquet")
        csv_data = pyarrow.csv.read_csv(
            input_file=csv_path,
            read_options=pyarrow.csv.ReadOptions(column_names=changeset_schema.names),
            parse_options=pyarrow.csv.ParseOptions(newlines_in_values=True, invalid_row_handler=invalid_row_handler),
            convert_options=pyarrow.csv.ConvertOptions(column_types=changeset_schema),
        )
        pyarrow.parquet.write_table(
            table=csv_data,
            where=parquet_path,
            # row_group_size=100000,
        )


def save_to_csv(xml_file: Path, output_dir: Path, chunk_size: int = 10000000):
    current_chunk = 0
    chunk_file_path = output_dir / f"{current_chunk}.csv"
    counter = 0
    csvfile = open(chunk_file_path, 'w', newline='')
    try:
        writer = csv.DictWriter(csvfile, fieldnames=changeset_schema.names)
        for changeset in parse_full_changeset_file(xml_file):
            writer.writerow(changeset.transform_to_dict())
            counter += 1
            if counter % 100000 == 0:
                logger.info(f"Processed {counter} rows in chunk {current_chunk}")
            if counter > chunk_size:
                csvfile.close()
                current_chunk += 1
                chunk_file_path = output_dir / f"{current_chunk}.csv"
                logger.info(f"writing chunk: {chunk_file_path}")
                csvfile = open(chunk_file_path, 'w', newline='')
                writer = csv.DictWriter(csvfile, fieldnames=changeset_schema.names)
                counter = 0
    finally:
        csvfile.close()


def upload_parquet(parquet_dir: Path) -> None:
    hook = S3Hook(aws_conn_id="aws_tt_s3")
    current_parquet_files = [file for file in hook.list_keys(bucket_name=s3_bucket_name, prefix="full/") if file.endswith("parquet")]
    hook.delete_objects(bucket=s3_bucket_name, keys=current_parquet_files)
    files_to_upload = list_files(directory=parquet_dir, extension="parquet")
    for file in files_to_upload:
        s3_key = f"full/{file.name}"
        logger.info(f"Uploading file: {file.as_posix()} to: s3://{s3_bucket_name}/{s3_key}")
        hook.load_file(
            bucket_name=s3_bucket_name,
            key=s3_key,
            filename=file,
        )
    hook.load_string(
        string_data=datetime.datetime.utcnow().isoformat(),
        bucket_name=s3_bucket_name,
        key="full/dag_run_date.txt",
        replace=True,
    )
    logger.info("Files uploaded to s3 successfully.")


default_args = {
    "retries": 2,
    "retry_delay": datetime.timedelta(minutes=15),
    "execution_timeout": datetime.timedelta(hours=12),
}

with DAG(
    dag_id="changesets_full_hist_file_to_parquet",
    description="Downloads changeset full history files and converts them to parquet.",
    start_date=datetime.datetime(2022, 11, 26),
    schedule_interval="0 7 * * 6",
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=datetime.timedelta(days=1),
    default_args=default_args,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    download_xml_file_task = BashOperator(
        task_id="download_xml_file",
        bash_command=f"""
            wget --quiet -O {temp_file_name.as_posix()} {file_url}
        """.strip(),
    )

    convert_xml_to_csv_task = PythonOperator(
        task_id="convert_xml_to_csv",
        python_callable=save_to_csv,
        op_kwargs={
            "xml_file": temp_file_name,
            "output_dir": temp_csv_dir,
            "chunk_size": 10000000,
        },
    )

    convert_csv_to_parquet_task = PythonOperator(
        task_id="convert_csv_to_parquet",
        python_callable=convert_csv_to_parquet,
        op_kwargs={
            "csv_dir": temp_csv_dir,
            "parquet_dir": temp_parquet_dir,
        },
    )

    upload_parquet_task = PythonOperator(
        task_id="upload_parquet",
        python_callable=upload_parquet,
        op_kwargs={
            "parquet_dir": temp_parquet_dir,
        }
    )

    delete_local_parquet_files = BashOperator(
        task_id="delete_parquet_files",
        bash_command=f"""
            rm -r {temp_parquet_dir.as_posix()}/*
        """.strip(),
    )

    delete_local_csv_files = BashOperator(
        task_id="delete_csv_files",
        bash_command=f"""
            rm -r {temp_csv_dir.as_posix()}/*
        """.strip(),
    )

    delete_xml_file_task = BashOperator(
        task_id="delete_xml_file",
        bash_command=f"""
            rm {temp_file_name.as_posix()}
        """.strip(),
    )

    chain(
        download_xml_file_task,
        convert_xml_to_csv_task,
        convert_csv_to_parquet_task,
        upload_parquet_task,
        [
            delete_xml_file_task,
            delete_local_parquet_files,
            delete_local_csv_files,
        ],
    )
