import os
from os.path import join, dirname, abspath
from typing import Union, Any, Dict, Optional, Tuple, List, Iterable, Callable
from datetime import datetime, timezone

import psycopg2 as pg
import psycopg2.extensions
import psycopg2.errors
from flask_restful import abort
from psycopg2.extras import execute_values, RealDictCursor
from dotenv import load_dotenv

QueryParametersType = Union[Iterable, Dict[str, Any]]
QueryOutputType = List[Optional[Tuple[Any]]]
PGCursor = psycopg2.extensions.cursor
PGConnection = psycopg2.extensions.connection


SQL_PATH = join(dirname(abspath(__file__)), 'queries')
QUERIES = {
    'addresses_all_where_geom': str(open(join(SQL_PATH, 'addresses_all_where_geom.sql'), 'r').read()),
    'addresses_where_geom': str(open(join(SQL_PATH, 'addresses_where_geom.sql'), 'r').read()),
    'buildings_all_where_geom': str(open(join(SQL_PATH, 'buildings_all_where_geom.sql'), 'r').read()),
    'buildings_where_geom': str(open(join(SQL_PATH, 'buildings_where_geom.sql'), 'r').read()),
    'cached_mvt': str(open(join(SQL_PATH, 'cached_mvt.sql'), 'r').read()),
    'delta_point_info': str(open(join(SQL_PATH, 'delta_point_info.sql'), 'r').read()),
    'mvt_insert': str(open(join(SQL_PATH, 'mvt_insert.sql'), 'r').read()),
    'mvt_add_to_reload_queue': str(open(join(SQL_PATH, 'mvt_add_to_reload_queue.sql'), 'r').read()),
    'locations_random': str(open(join(SQL_PATH, 'locations_random.sql'), 'r').read()),
    'locations_most_count': str(open(join(SQL_PATH, 'locations_most_count.sql'), 'r').read()),
    'processes': str(open(join(SQL_PATH, 'processes.sql'), 'r').read()),
    'insert_to_exclude_prg': str(open(join(SQL_PATH, 'insert_to_exclude_prg.sql'), 'r').read()),
    'insert_to_exclude_prg_addresses_where_geom': str(open(join(SQL_PATH, 'insert_to_exclude_prg_addresses_where_geom.sql'), 'r').read()),
    'insert_to_exclude_bdot_buildings': str(open(join(SQL_PATH, 'insert_to_exclude_bdot_buildings.sql'), 'r').read()),
    'insert_to_exclude_bdot_buildings_where_geom': str(open(join(SQL_PATH, 'insert_to_exclude_bdot_buildings_where_geom.sql'), 'r').read()),
    'insert_to_package_exports': str(open(join(SQL_PATH, 'insert_to_package_exports.sql'), 'r').read()),
    'latest_updates': str(open(join(SQL_PATH, 'latest_updates.sql'), 'r').read()),
    'sc_proposed_addresses_in_bbox': str(open(join(SQL_PATH, 'sc_proposed_addresses_in_bbox.sql'), 'r').read()),
    'sc_proposed_buildings_in_bbox': str(open(join(SQL_PATH, 'sc_proposed_buildings_in_bbox.sql'), 'r').read()),
    'streets_all_where_geom': str(open(join(SQL_PATH, 'streets_all_where_geom.sql'), 'r').read()),
    'admin_geom_where_simc': str(open(join(SQL_PATH, 'admin_geom_where_simc.sql'), 'r').read()),
    'admin_geom_where_terc': str(open(join(SQL_PATH, 'admin_geom_where_terc.sql'), 'r').read()),
    'admin_geom_where_id': str(open(join(SQL_PATH, 'admin_geom_where_id.sql'), 'r').read()),
    'josm_nearest_building': str(open(join(SQL_PATH, 'josm_nearest_building.sql'), 'r').read()),
    'josm_nearest_building_geojson': str(open(join(SQL_PATH, 'josm_nearest_building_geojson.sql'), 'r').read()),
    'josm_nearest_building_geom_only': str(open(join(SQL_PATH, 'josm_nearest_building_geom_only.sql'), 'r').read()),
}


def get_dsn(dotenv_file_path: str = '/opt/gugik2osm/conf/.env', read_only_user: bool = False) -> str:
    """Method reads connection parameters from .env file and returns dsn (connection string) for psycopg2."""

    load_dotenv(dotenv_file_path, verbose=True)
    host = os.environ['PGHOSTADDR']
    port = os.environ['PGPORT']
    database = os.environ['PGDATABASE']
    user = os.environ['PGUSER'] if not read_only_user else os.environ['PGUSER_RO']
    password = os.environ['PGPASSWORD'] if not read_only_user else os.environ['PGPASSWORD_RO']
    dsn = f'host={host} port={port} dbname={database} user={user} password={password}'

    return dsn


def pgdb() -> PGConnection:
    """Method returns connection to the DB."""

    connection = pg.connect(dsn=get_dsn())
    cur = connection.cursor()
    cur.execute(f'SET statement_timeout={1000 * 60};')
    connection.commit()
    cur.close()
    return connection


def pgdb_read_only() -> PGConnection:
    """Method returns read-only connection to the DB."""

    connection_read_only = pg.connect(dsn=get_dsn(read_only_user=True))
    connection_read_only.set_session(readonly=True, autocommit=True)
    cur = connection_read_only.cursor()
    cur.execute(f'SET statement_timeout={1000 * 60};')
    return connection_read_only


def is_db_locked() -> bool:
    """Checks if db_lock record in process_locks is active."""

    connection = pgdb_read_only()
    query = "SELECT in_progress FROM process_locks WHERE process_name = 'db_lock';"
    cur = connection.cursor()
    cur.execute(query)
    is_locked = cur.fetchall()[0][0]
    connection.close()
    return is_locked


def abort_if_db_locked() -> None:
    """Executes flask abort if the database is locked."""

    if is_db_locked():
        abort(503)


def data_from_db(
    query: str,
    parameters: QueryParametersType = None,
    row_as: Union[tuple, dict, Callable] = tuple,
    bypass_lock: bool = False
) -> List[Union[tuple, dict, Any]]:
    """Method executes SQL query and returns data. Data can be mapped to class if you provide it in row_as parameter.
    Provides error handling. In case of exception it rolls back transaction and closes the connection."""

    if not bypass_lock:
        abort_if_db_locked()

    connection = pgdb_read_only()

    if row_as == dict:
        cursor_factory_type = RealDictCursor
    else:
        cursor_factory_type = None

    cur = connection.cursor(cursor_factory=cursor_factory_type)
    cur.execute(query, parameters) if parameters else cur.execute(query)
    results = cur.fetchall()
    connection.close()
    if row_as not in (dict, tuple):
        results = [row_as(*row) for row in results]
    return results


def execute_query(query: str, parameters: QueryParametersType = None, bypass_lock: bool = False) -> List[tuple]:
    """Method executes SQL query and commits transaction. Provides error handling.
    In case of exception it rolls back transaction and closes the connection."""

    if not bypass_lock:
        abort_if_db_locked()

    connection = pgdb()

    with connection.cursor() as cur:
        try:
            cur.execute(query, parameters) if parameters else cur.execute(query)
        except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            print(e)
            raise
        except:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            if connection:
                connection.rollback()
                connection.close()
            raise
        try:
            results = cur.fetchall()
        except psycopg2.ProgrammingError:
            results = []
        connection.commit()
        return results


def execute_batch(query: str, parameters: List[QueryParametersType], bypass_lock: bool = False) -> List[tuple]:
    """Execute query using VALUES with a sequence of parameters.
    In simpler terms it allows e.g. batch inserts such as:
        insert into table values (1, 'a'), (2, 'b');
    instead of having to execute inserts separately:
        insert into table values (1, 'a');
        insert into table values (2, 'b');
    This can provide significant performance boost.
    """

    if not bypass_lock:
        abort_if_db_locked()

    connection = pgdb()

    with connection.cursor() as cur:
        try:
            execute_values(cur, query, parameters)
        except psycopg2.InterfaceError:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            raise
        except:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            if connection:
                connection.rollback()
                connection.close()
            raise
        try:
            results = cur.fetchall()
        except psycopg2.ProgrammingError:
            results = []
        connection.commit()
        return results
