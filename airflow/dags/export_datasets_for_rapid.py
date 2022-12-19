import datetime
from functools import partial

from airflow import DAG
from airflow.operators.bash import BashOperator

from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


addresses_query = """
select 
	row_number() over() as ADDR_RECNO,
	nr as addr_housenumber,
	teryt_ulica as addr_street,
	null::text as addr_unit,
	case when teryt_ulica is null then null::text else teryt_msc end addr_city,
	case when teryt_ulica is not null then null::text else teryt_msc end addr_place,
	null::text as addr_state,
	pna as addr_postcode,
	'gugik.gov.pl' as source,
	st_transform(geom, 4326) as geom 
from prg.delta d
left join exclude_prg on d.lokalnyid=exclude_prg.id
where exclude_prg.id is null
""".strip().replace("\n", " ").replace(" " * 2, " ")

buildings_query = """
select
	row_number() over() as BLDG_RECNO,
	building,
	amenity,
	man_made,
	leisure,
	tourism,
	historic,
	null::text as name,
	null::text as height,
	building_levels as levels,
	null::text as start_date,
	'www.geoportal.gov.pl' as source,
	geom_4326 as geom
from bdot_buildings b
left join exclude_bdot_buildings ex on b.lokalnyid=ex.id
where ex.id is null and building is not null
""".strip().replace("\n", " ").replace(" " * 2, " ")


with DAG(
    dag_id="export_datasets_for_rapid",
    description="Exports datasets to be included in RapiD by ESRI.",
    start_date=datetime.datetime(2022, 12, 19),
    schedule_interval=None,
    catchup=False,
    # on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    export_addresses = BashOperator(
        task_id="export_addresses",
        bash_command=f"""
        # exit on error in any command
        set -e
        
        set -a
        source /opt/gugik2osm/conf/.env
        set +a
        
        echo "writing to geopackage"
        ogr2ogr -f "GPKG" \
            /opt/gugik2osm/temp/export/addresses_for_rapid.gpkg \
            PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" \
            -sql "{addresses_query}" \
            -gt 65536 --config OGR_SQLITE_CACHE=1000 --config OGR_SQLITE_SYNCHRONOUS=OFF
        echo "vacuum"
        ogrinfo /opt/gugik2osm/temp/export/addresses_for_rapid.gpkg -sql "VACUUM"
        echo "analyze"
        ogrinfo /opt/gugik2osm/temp/export/addresses_for_rapid.gpkg -sql "ANALYZE"
        echo "ogr2ogr done"
        """.strip(),
    )
    move_addresses_file = BashOperator(
        task_id="move_addresses_file",
        bash_command="mv /opt/gugik2osm/temp/export/addresses_for_rapid.gpkg /var/www/data/addresses_for_rapid.gpkg",
    )

    export_buildings = BashOperator(
        task_id="export_buildings",
        bash_command=f"""
        # exit on error in any command
        set -e

        set -a
        source /opt/gugik2osm/conf/.env
        set +a

        echo "writing to geopackage"
        ogr2ogr -f "GPKG" \
            /opt/gugik2osm/temp/export/buildings_for_rapid.gpkg \
            PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" \
            -sql "{buildings_query}" \
            -gt 65536 --config OGR_SQLITE_CACHE=1000 --config OGR_SQLITE_SYNCHRONOUS=OFF
        echo "vacuum"
        ogrinfo /opt/gugik2osm/temp/export/buildings_for_rapid.gpkg -sql "VACUUM"
        echo "analyze"
        ogrinfo /opt/gugik2osm/temp/export/buildings_for_rapid.gpkg -sql "ANALYZE"
        echo "ogr2ogr done"
        """.strip(),
    )
    move_buildings_file = BashOperator(
        task_id="move_addresses_file",
        bash_command="mv /opt/gugik2osm/temp/export/buildings_for_rapid.gpkg /var/www/data/buildings_for_rapid.gpkg",
    )

    export_addresses >> move_addresses_file
    export_buildings >> move_buildings_file
