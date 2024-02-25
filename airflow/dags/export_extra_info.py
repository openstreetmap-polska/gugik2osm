import datetime
from functools import partial
from  pathlib import Path

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


query_export_max_addr_version = """
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

file_name_max_addr_version = "municipality_max_addr_ver.csv"

query_export_no_of_rejected_addr_per_muni = """
COPY(
    select 
        pa.jednostkaadministracyjna_01 as woj,
        pa.jednostkaadministracyjna_02 as pow,
        pa.jednostkaadministracyjna_03 as gmi,
        adm.idteryt as teryt_id,
        count(*) as number_of_addresses
    from prg.punkty_adresowe pa
    join prg.jednostki_administracyjne adm on pa.komponent_03=adm.gmlid
    left join addresses a on pa.lokalnyid::uuid=a.lokalnyid
    where 1=1
        and a.lokalnyid is null
        and pa.status ='istniejacy'
    group by 1, 2, 3, 4
    order by number_of_addresses desc
) TO STDOUT (FORMAT CSV, HEADER true);
""".strip().replace("\n", " ").replace(" " * 2, " ")

file_name_no_of_rejected_addr_per_muni = "municipality_rejected_addr_count.csv"

query_export_rejected_addresses = """
COPY(
    select 
        adm.idteryt as teryt_id_gmina,
        adm.nazwa as nazwa_gmina,
        m.idteryt as teryt_id_miejscowosc,
        m.nazwa as nazwa_miejscowosc,
        ul.idteryt as teryt_id_ulica,
        ul.nazwaglownaczesc as nazwa_ulica,
        pa.*
    from prg.punkty_adresowe pa
    left join prg.jednostki_administracyjne adm on pa.komponent_03=adm.gmlid
    left join prg.miejscowosci m on pa.komponent_04=m.gmlid
    left join prg.ulice ul on pa.komponent_05=ul.gmlid
    left join addresses a on pa.lokalnyid::uuid=a.lokalnyid
    where 1=1
        and a.lokalnyid is null
        and pa.status ='istniejacy'
    order by adm.idteryt
) TO STDOUT (FORMAT CSV, HEADER true);
""".strip().replace("\n", " ").replace(" " * 2, " ")

file_name_rejected_addresse = "municipality_rejected_addressses.csv"

export_command = """
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
    description="Exports info about max addr version (timestamp) per municipality and some other stuff.",
    start_date=datetime.datetime(2024, 2, 19),
    schedule_interval="@weekly",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    start_task = EmptyOperator(task_id="start")
    end_task = EmptyOperator(task_id="end")

    # max address version per municipality
    export_max_addr_version_task = BashOperator(
        task_id="export_max_addr_version",
        bash_command=export_command.format(query=query_export_max_addr_version, file_name=file_name_max_addr_version),
    )
    move_file_export_max_addr_version_task = BashOperator(
        task_id="move_file_export_max_addr_version",
        bash_command=f"mv /opt/gugik2osm/temp/export/{file_name_max_addr_version} /var/www/data/{file_name_max_addr_version}",
    )

    # rejected addresses count per municipality
    export_rejected_addresses_count_task = BashOperator(
        task_id="export_rejected_addresses_count",
        bash_command=export_command.format(query=query_export_no_of_rejected_addr_per_muni, file_name=file_name_no_of_rejected_addr_per_muni),
    )
    move_file_rejected_addresses_count_task = BashOperator(
        task_id="move_file_rejected_addresses_count",
        bash_command=f"mv /opt/gugik2osm/temp/export/{file_name_no_of_rejected_addr_per_muni} /var/www/data/{file_name_no_of_rejected_addr_per_muni}",
    )

    # rejected addresses
    export_rejected_addresses_task = BashOperator(
        task_id="export_rejected_addresses",
        bash_command=export_command.format(query=query_export_rejected_addresses, file_name=file_name_rejected_addresse),
    )
    move_file_rejected_addresses_task = BashOperator(
        task_id="move_file_rejected_addresses",
        bash_command=f"mv /opt/gugik2osm/temp/export/{file_name_rejected_addresse} /var/www/data/{file_name_rejected_addresse}",
    )

    # task dependencies
    chain(
        start_task,
        [
            export_max_addr_version_task,
            export_rejected_addresses_count_task,
            export_rejected_addresses_task,
        ],
        [
            move_file_export_max_addr_version_task,
            move_file_rejected_addresses_count_task,
            move_file_rejected_addresses_task,
        ],
        end_task
    )
