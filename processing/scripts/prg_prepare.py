import argparse
import time
from datetime import datetime, timezone, timedelta
from os.path import join, dirname, abspath
from os import walk
from typing import Union

import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sql_path = abspath(join(dirname(abspath(__file__)), '..', 'sql'))
ddl_path = join(sql_path, 'ddl')
dml_path = join(sql_path, 'dml')
partial_update_path = join(sql_path, 'partial_update')


def _read_and_execute(
    conn,
    path: str,
    vacuum: bool = True,
    temp_set_workmem: str = None,
    query_parameters: Union[tuple, dict, None] = None
) -> None:
    """Internal method that reads sql query from file, connects to the database, and executes it."""

    print(datetime.now(timezone.utc).astimezone().isoformat(), '- executing script:', path)
    # start counter to measure execution time
    sts = time.perf_counter()

    cur = conn.cursor()
    sql = open(path, 'r', encoding='UTF-8').read()
    if temp_set_workmem is not None:
        cur.execute('show work_mem')
        old_workmem: str = cur.fetchall()[0][0]
        print('old work_mem:', old_workmem, '- setting to:', temp_set_workmem)
        cur.execute('set work_mem = %s', (temp_set_workmem,))
    if query_parameters:
        cur.execute(sql, query_parameters)
    else:
        cur.execute(sql)
    conn.commit()
    if temp_set_workmem is not None:
        print('Setting work_mem back to the previous value:', old_workmem)
        cur.execute('set work_mem = %s', (old_workmem,))
        conn.commit()
    if vacuum:
        print('Vacuum analyze.')
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur.execute('VACUUM ANALYZE;')
        conn.set_isolation_level(old_isolation_level)

    ets = time.perf_counter()
    delta = ets - sts
    print(datetime.now(timezone.utc).astimezone().isoformat(),
          '- finished executing:', path,
          '- ex. time:', str(timedelta(seconds=delta)))


def execute_scripts_from_files(
        dsn: str,
        paths: Union[str, list, tuple],
        vacuum: bool = True,
        temp_set_workmem: str = None,
        query_parameters: Union[tuple, dict, None] = None
) -> None:
    """Method executes sql script from given file path(s)."""

    if len(paths) == 0:
        raise AttributeError('You need to specify at least one path for file with an sql script.')
    with pg.connect(dsn) as conn:
        if type(paths) == str:
            _read_and_execute(conn, paths, vacuum, temp_set_workmem)
        elif type(paths) in (tuple, list):
            if type(paths[0]) in (tuple, list):
                for lst in paths:
                    for path in lst:
                        _read_and_execute(conn, path, vacuum, temp_set_workmem, query_parameters)
            else:
                for path in paths:
                    _read_and_execute(conn, path, vacuum, temp_set_workmem, query_parameters)
        else:
            raise AttributeError(f'Wrong arguments should be strings with paths or list of strings (paths): {paths}')


def full_process(dsn: str) -> None:
    ddls = []
    dmls = []
    # get paths of sql files
    # r=root, d=directories, f = files
    for r, d, f in walk(ddl_path):
        for file in f:
            if '.sql' in file:
                ddls.append(join(r, file))
    for r, d, f in walk(dml_path):
        for file in f:
            if '.sql' in file:
                dmls.append(join(r, file))
    # make sure dml files are sorted by names, ddl files should not require any specific order
    dmls = [x for x in sorted(dmls)]

    # execute sql scripts
    # execute_scripts_from_files(dsn=dsn, vacuum=True, paths=[ddls, dmls])
    execute_scripts_from_files(dsn=dsn, vacuum=True, paths=ddls)
    execute_scripts_from_files(dsn=dsn, vacuum=True, paths=dmls, temp_set_workmem='2048MB')


def partial_update(dsn: str, bbox: dict) -> None:
    sql_queries = []
    # get paths of sql files
    # r=root, d=directories, f = files
    for r, d, f in walk(ddl_path):
        for file in f:
            if '.sql' in file:
                sql_queries.append(join(r, file))
    sql_queries = [x for x in sorted(sql_queries)]
    execute_scripts_from_files(dsn=dsn, vacuum=False, paths=sql_queries, query_parameters=bbox)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', help='Launch full process', nargs='?', const=True)
    parser.add_argument('--update', help='Launch partial update process', nargs='?', const=True)
    parser.add_argument('--bbox', help='Bounding box for update. Provide 4 parameters: xmin, ymin, xmax, ymax', nargs=4)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL DB.', nargs=1)
    args = vars(parser.parse_args())

    if args['full']:
        full_process(args['dsn'][0])
    elif args['update']:
        bbox = {
            'xmin': float(args['bbox'][0]),
            'ymin': float(args['bbox'][1]),
            'xmax': float(args['bbox'][2]),
            'ymax': float(args['bbox'][3])
        }
        partial_update(args['dsn'][0], bbox)
