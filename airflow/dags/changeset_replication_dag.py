import datetime
import logging
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

from airflow import DAG, AirflowException
from airflow.models import Variable, TaskInstance
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator, ShortCircuitOperator

from utils.osm.changesets import find_newest_changeset_replication_sequence
from utils.discord import send_dag_run_status

logger = logging.getLogger()

send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)

last_processed_sequence_variable_name = "last_processed_changeset_sequence"


def check_if_anything_to_run(**kwargs) -> bool:
    last_processed: str = Variable.get(last_processed_sequence_variable_name)
    if last_processed is None:
        raise AirflowException(f"Variable: {last_processed_sequence_variable_name} does not exist.")
    newest = find_newest_changeset_replication_sequence()
    ti: TaskInstance = kwargs["ti"]
    ti.xcom_push(key="changeset_replication_sequence", value=newest.as_json_str())
    return newest.formatted > last_processed


def process_changesets(**kwargs) -> None:
    import duckdb
    import pyarrow as pa
    import pyarrow.parquet as pq

    from utils.osm.changesets import changesets_between_sequences
    from utils.osm.replication import replication_sequence_from_json_str
    from utils.parquet import changeset_schema

    last_processed: str = Variable.get(last_processed_sequence_variable_name, "")  # we check if variable has value in previous task
    ti: TaskInstance = kwargs["ti"]
    newest = replication_sequence_from_json_str(
        ti.xcom_pull(task_ids="check_if_anything_to_process", key="changeset_replication_sequence")
    )

    logger.info(f"Processing files from: {last_processed} to: {newest.formatted}")
    changesets = changesets_between_sequences(last_processed, newest.number)
    data = [changeset.transform_to_dict(tags_for_arrow_map=True) for changeset in changesets]
    arrow_table = pa.Table.from_pylist(data, changeset_schema)
    logger.info(f"Converted changesets to PyArrow Table with: {arrow_table.num_rows} rows.")
    conn = duckdb.connect()

    processed_datetime = ti.start_date
    date_str = processed_datetime.date().isoformat()
    public_dir = Path("/var/www/data/changesets/")
    opened_last_hour = "opened_last_hour"
    last_hour_path = public_dir / f"{opened_last_hour}.parquet"
    opened_last_24h = "opened_last_24h"
    last_24h_path = public_dir / f"{opened_last_24h}.parquet"
    state_path = public_dir / "state.txt"
    processed_at_path = public_dir / "processed_at.txt"
    latest_path = public_dir / "latest.parquet"

    with TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        latest_temp_path = temp_dir / "latest.parquet"
        last_hour_temp_path = temp_dir / f"{opened_last_hour}.parquet"
        last_24h_temp_path = temp_dir / f"{opened_last_24h}.parquet"
        state_temp_path = temp_dir / "state.txt"
        processed_at_temp_path = temp_dir / "processed_at.txt"

        with open(state_temp_path, "w", encoding="utf-8") as f:
            f.write(newest.formatted)

        with open(processed_at_temp_path, "w", encoding="utf-8") as f:
            f.write(date_str)

        conn.execute(
            f"COPY (SELECT * FROM arrow_table) TO '{latest_temp_path.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )

        if last_hour_path.is_file():
            last_hour_table = pq.read_table(last_hour_path.as_posix())
            conn.execute(f"""
                COPY (
                    WITH
                    raw as (
                        SELECT * FROM arrow_table
                        UNION ALL
                        SELECT * FROM last_hour_table
                    ),
                    last_h as (
                        SELECT * FROM raw WHERE created_at > (CURRENT_TIMESTAMP - '1 hour'::interval)
                    )
                    SELECT DISTINCT ON (id) * FROM last_h ORDER BY closed_at DESC NULLS LAST
                ) TO '{last_hour_temp_path.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)
                """
            )
        else:
            conn.execute(
                f"COPY (SELECT * FROM arrow_table) TO '{last_hour_temp_path.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )

        if last_24h_path.is_file():
            last_24h_table = pq.read_table(last_24h_path.as_posix())
            conn.execute(f"""
                COPY (
                    WITH
                    raw as (
                        SELECT * FROM arrow_table
                        UNION ALL
                        SELECT * FROM last_24h_table
                    ),
                    last_24h as (
                        SELECT * FROM raw WHERE created_at > (CURRENT_TIMESTAMP - '24 hours'::interval)
                    )
                    SELECT DISTINCT ON (id) * FROM last_24h ORDER BY closed_at DESC NULLS LAST
                ) TO '{last_24h_temp_path.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)
                """
            )
        else:
            conn.execute(
                f"COPY (SELECT * FROM arrow_table) TO '{last_24h_temp_path.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )

        logger.info("Temp files saved. Overwriting old files.")
        latest_temp_path.replace(latest_path)
        last_hour_temp_path.replace(last_hour_path)
        last_24h_temp_path.replace(last_24h_path)
        state_temp_path.replace(state_path)
        processed_at_temp_path.replace(processed_at_path)
        logger.info("Files moved.")

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
