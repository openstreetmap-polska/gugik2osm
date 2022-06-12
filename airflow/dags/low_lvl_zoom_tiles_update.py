import datetime
from functools import partial

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


with DAG(
    dag_id="low_lvl_zoom_tiles_update",
    description="Refresh tiles on zoom levels 6 and 7.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="@hourly",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    PostgresOperator(
        task_id="refresh_low_lvl_zoom_tiles",
        sql="""
            create temporary table tt (z int, x int, y int, mvt bytea);
            insert into tt select z, x, y, mvt(z, x, y) from tiles where z in (6, 7);
            analyze tt;
            update tiles set mvt = tt.mvt from tt where tiles.z=tt.z and tiles.x=tt.x and tiles.y=tt.y;
            drop table tt;
        """,
        autocommit=True,
    )
