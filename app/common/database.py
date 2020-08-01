from os import environ
from os.path import join, dirname, abspath
import atexit
from typing import Union
from datetime import datetime, timezone

import psycopg2 as pg
import psycopg2.extensions
import psycopg2.errors
from psycopg2.extras import execute_values


SQL_PATH = join(dirname(abspath(__file__)), 'queries')
QUERIES = {
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
    'insert_to_exclude_lod1': str(open(join(SQL_PATH, 'insert_to_exclude_lod1.sql'), 'r').read()),
    'delete_tiles_excluded_prg': str(open(join(SQL_PATH, 'delete_tiles_excluded_prg.sql'), 'r').read()),
    'delete_tiles_excluded_lod1': str(open(join(SQL_PATH, 'delete_tiles_excluded_lod1.sql'), 'r').read()),
}
conn: psycopg2.extensions.connection = None


def pgdb() -> psycopg2.extensions.connection:
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


def execute_sql(cursor, query: str, parameters: Union[tuple, dict] = None):
    """Method executes SQL query in a given cursor with given parameters. Provides error handling.
    In case of exception it rolls back transaction and closes the connection."""
    try:
        cursor.execute(query, parameters) if parameters else cursor.execute(query)
    except:
        global conn
        print(datetime.now(timezone.utc).astimezone().isoformat(),
              f'- Error while executing query: {query}, with parameters: {parameters}')
        conn.rollback()
        conn.close()
        conn = None
        raise
    return cursor
