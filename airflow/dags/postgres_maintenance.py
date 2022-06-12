import datetime
from functools import partial

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator

from utils.discord import send_dag_run_status


send_dag_run_status_to_discord = partial(send_dag_run_status, antispam=False)


with DAG(
    dag_id="postgresql_maintenance_tasks",
    description="Run VACUUM ANALYZE in PostgreSQL database and create backups.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="10 4 * * TUE",
    catchup=False,
    on_failure_callback=send_dag_run_status_to_discord,
) as dag:

    vacuum_analyze_task = BashOperator(
        task_id="vacuum_analyze",
        bash_command='sudo -u postgres psql -d gugik2osm -c "VACUUM ANALYZE"'
    )

    create_schema_backup = BashOperator(
        task_id="schema_backup",
        bash_command='''
            set -e;
            sudo -u postgres pg_dump --format p --schema-only --no-owner --no-privileges --file /opt/gugik2osm/temp/export/db_only_schema.sql --dbname gugik2osm;
            sudo -u postgres mv /opt/gugik2osm/temp/export/db_only_schema.sql /var/www/data/dbbackup/db_only_schema.sql;
        '''.strip()
    )

    create_data_backup = BashOperator(
        task_id="data_backup",
        bash_command='''
            set -e;
            sudo -u postgres pg_dump --format c --compress 9 --no-owner --no-privileges --file /opt/gugik2osm/temp/export/db.bak --dbname gugik2osm;
            sudo -u postgres mv /opt/gugik2osm/temp/export/db.bak /var/www/data/dbbackup/db.bak;
        '''.strip()
    )

    chain(
        vacuum_analyze_task,
        create_schema_backup,
        create_data_backup,
    )
