import datetime
from functools import partial
from  pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


query = """
COPY(
    select 
        pa.jednostkaadministracyjna_01 as woj,
        pa.jednostkaadministracyjna_02 as pow,
        pa.jednostkaadministracyjna_03 as gmi,
        a.idteryt as teryt_id,
        max(pa.wersjaid) as max_wersjaid
    from prg.punkty_adresowe pa
    join prg.jednostki_administracyjne a on pa.komponent_03=a.gmlid
    group by 1, 2, 3, 4
    order by max_wersjaid
) TO STDOUT (FORMAT CSV, HEADER true);
""".strip().replace("\n", " ").replace(" " * 2, " ")

file_name = "municipality_max_addr_ver.csv"

export_command = f"""
# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

echo "writing to csv"
psql "dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" \
    -c "{query}" \
    > /opt/gugik2osm/temp/export/{file_name}
""".lstrip()


with DAG(
    dag_id=Path(__file__).stem,
    description="Exports info about max addr version (timestamp) per municipality.",
    start_date=datetime.datetime(2024, 2, 19),
    schedule_interval="@weekly",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:


    export_task = BashOperator(
        task_id="export",
        bash_command=export_command,
    )
    move_file_task = BashOperator(
        task_id="move_file",
        bash_command=f"mv /opt/gugik2osm/temp/export/{file_name} /var/www/data/{file_name}",
    )

    export_task >> move_file_task
