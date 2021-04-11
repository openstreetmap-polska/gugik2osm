from os import environ
from os.path import join, dirname, abspath
import atexit
from typing import Union, Any, Dict, Optional, Tuple, List, Iterable
from datetime import datetime, timezone

import psycopg2 as pg
import psycopg2.extensions
import psycopg2.errors
from psycopg2.extras import execute_values

QueryParametersType = Union[Iterable, Dict[str, Any]]
QueryOutputType = List[Optional[Tuple[Any]]]
PGCursor = psycopg2.extensions.cursor
PGConnection = psycopg2.extensions.connection


SQL_PATH = join(dirname(abspath(__file__)), 'queries')
QUERIES = {
    'buildings_all_bbox': str(open(join(SQL_PATH, 'buildings_all_bbox.sql'), 'r').read()),
    'buildings_all_id': str(open(join(SQL_PATH, 'buildings_all_id.sql'), 'r').read()),
    'buildings_vertices': str(open(join(SQL_PATH, 'buildings_vertices.sql'), 'r').read()),
    'buildings_vertices_where_id': str(open(join(SQL_PATH, 'buildings_vertices_where_id.sql'), 'r').read()),
    'cached_mvt': str(open(join(SQL_PATH, 'cached_mvt.sql'), 'r').read()),
    'delta_point_info': str(open(join(SQL_PATH, 'delta_point_info.sql'), 'r').read()),
    'delta_where_bbox': str(open(join(SQL_PATH, 'delta_where_bbox.sql'), 'r').read()),
    'delta_where_id': str(open(join(SQL_PATH, 'delta_where_id.sql'), 'r').read()),
    'mvt_hl': str(open(join(SQL_PATH, 'mvt_hl.sql'), 'r').read()),
    'mvt_ll': str(open(join(SQL_PATH, 'mvt_ll.sql'), 'r').read()),
    'mvt_ll_aggr_simc': str(open(join(SQL_PATH, 'mvt_ll_aggr_simc.sql'), 'r').read()),
    'mvt_ll_aggr_simc_ulic': str(open(join(SQL_PATH, 'mvt_ll_aggr_simc_ulic.sql'), 'r').read()),
    'mvt_ll_aggr_terc': str(open(join(SQL_PATH, 'mvt_ll_aggr_terc.sql'), 'r').read()),
    'locations_random': str(open(join(SQL_PATH, 'locations_random.sql'), 'r').read()),
    'locations_most_count': str(open(join(SQL_PATH, 'locations_most_count.sql'), 'r').read()),
    'processes': str(open(join(SQL_PATH, 'processes.sql'), 'r').read()),
    'insert_to_exclude_prg': str(open(join(SQL_PATH, 'insert_to_exclude_prg.sql'), 'r').read()),
    'insert_to_exclude_bdot_buildings': str(open(join(SQL_PATH, 'insert_to_exclude_bdot_buildings.sql'), 'r').read()),
    'insert_to_package_exports': str(open(join(SQL_PATH, 'insert_to_package_exports.sql'), 'r').read()),
    'latest_updates': str(open(join(SQL_PATH, 'latest_updates.sql'), 'r').read()),
    'sc_proposed_addresses_in_bbox': str(open(join(SQL_PATH, 'sc_proposed_addresses_in_bbox.sql'), 'r').read()),
    'sc_proposed_buildings_in_bbox': str(open(join(SQL_PATH, 'sc_proposed_buildings_in_bbox.sql'), 'r').read()),
}
conn: Union[PGConnection, None] = None


def pgdb() -> PGConnection:
    """Method returns connection to the DB. If there is no connection active it creates one."""
    global conn
    if conn:
        return conn
    else:
        conn = pg.connect(dsn=environ['dsn'])
        return conn


@atexit.register
def close_db_connection():
    """Close the database connection. Method executed upon exit."""
    global conn
    if conn:
        conn.close()


def execute_sql(cursor: PGCursor, query: str, parameters: QueryParametersType = None) -> PGCursor:
    """Method executes SQL query in a given cursor with given parameters. Provides error handling.
    In case of exception it rolls back transaction and closes the connection."""
    global conn
    try:
        cursor.execute(query, parameters) if parameters else cursor.execute(query)
    except psycopg2.InterfaceError:
        print(datetime.now(timezone.utc).astimezone().isoformat(),
              f'- Error while executing query: {query}, with parameters: {parameters}')
        conn = None
        raise
    except:
        print(datetime.now(timezone.utc).astimezone().isoformat(),
              f'- Error while executing query: {query}, with parameters: {parameters}')
        if conn:
            conn.rollback()
            conn.close()
        conn = None
        raise
    return cursor


def data_from_db(query: str, parameters: QueryParametersType = None) -> List[tuple]:
    """Method executes SQL query in a given cursor with given parameters. Provides error handling.
    In case of exception it rolls back transaction and closes the connection."""

    global conn
    connection = pgdb()
    with connection.cursor() as cur:
        try:
            cur.execute(query, parameters) if parameters else cur.execute(query)
        except psycopg2.InterfaceError:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            conn = None
            raise
        except:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            if connection:
                connection.rollback()
                connection.close()
            conn = None
            raise
        return cur.fetchall()


def execute_query(query: str, parameters: QueryParametersType = None) -> List[tuple]:
    """Method executes SQL query in a given cursor with given parameters. Provides error handling.
    In case of exception it rolls back transaction and closes the connection."""

    global conn
    connection = pgdb()
    with connection.cursor() as cur:
        try:
            cur.execute(query, parameters) if parameters else cur.execute(query)
        except psycopg2.InterfaceError:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            conn = None
            raise
        except:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            if connection:
                connection.rollback()
                connection.close()
            conn = None
            raise
        connection.commit()
        try:
            results = cur.fetchall()
        except psycopg2.ProgrammingError:
            results = []
        return results


def execute_batch(query: str, parameters: List[QueryParametersType]) -> List[tuple]:

    global conn
    connection = pgdb()
    with connection.cursor() as cur:
        try:
            execute_values(cur, query, parameters)
        except psycopg2.InterfaceError:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            conn = None
            raise
        except:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  f'- Error while executing query: {query}, with parameters: {parameters}')
            if connection:
                connection.rollback()
                connection.close()
            conn = None
            raise
        connection.commit()
        try:
            results = cur.fetchall()
        except psycopg2.ProgrammingError:
            results = []
        return results
