import argparse
import time
from datetime import datetime, timezone
from os.path import join, dirname, abspath
from os import walk
from typing import Union

import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sql_path = abspath(join(dirname(abspath(__file__)), '..', 'sql'))
ddl_path = join(sql_path, 'ddl')
dml_path = join(sql_path, 'dml')


def _read_and_execute(conn, path: str, vacuum: bool = True) -> None:
    print(datetime.now(timezone.utc).astimezone().isoformat(), '- executing script:', path)
    # start counter to measure execution time
    sts = time.perf_counter()

    cur = conn.cursor()
    sql = open(path, 'r', encoding='UTF-8').read()
    cur.execute(sql)
    conn.commit()
    if vacuum:
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur.execute('VACUUM ANALYZE;')
        conn.set_isolation_level(old_isolation_level)

    ets = time.perf_counter()
    delta = ets - sts
    print(datetime.now(timezone.utc).astimezone().isoformat(), '- finished executing:', path, '- ex. time:', delta)


def execute_scripts_from_files(dsn: str, paths: Union[str, list, tuple], vacuum: bool = True) -> None:
    if len(paths) == 0:
        raise AttributeError('You need to specify at least one path for file with an sql script.')
    with pg.connect(dsn) as conn:
        if type(paths[0]) == str:
            _read_and_execute(conn, paths, vacuum)
        elif type(paths[0]) in (tuple, list):
            for lst in paths:
                for path in lst:
                    _read_and_execute(conn, path, vacuum)
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
    execute_scripts_from_files(dsn=dsn, vacuum=True, paths=[ddls, dmls])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', help='Launch full process', nargs='?', const=True)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL DB.', nargs=1)
    args = vars(parser.parse_args())

    if args['full']:
        full_process(args['dsn'][0])
