import argparse
import time
from datetime import datetime, timezone, timedelta
from os.path import join, dirname, abspath
from os import walk
from typing import Union

import mercantile as m
from pyproj import Proj, transform
import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sql_path = abspath(join(dirname(abspath(__file__)), '..', 'sql'))
ddl_path = join(sql_path, 'ddl')
dml_path = join(sql_path, 'dml')
partial_update_path = join(sql_path, 'partial_update')


def to_merc(bbox: m.LngLatBbox) -> dict:
    in_proj = Proj('epsg:4326')
    out_proj = Proj('epsg:3857')
    res = dict()
    res["west"], res["south"] = transform(in_proj, out_proj, bbox.south, bbox.west)
    res["east"], res["north"] = transform(in_proj, out_proj, bbox.north, bbox.east)
    return res


def _read_and_execute(
    conn,
    path: str,
    vacuum: str = 'once',
    temp_set_workmem: str = None,
    query_parameters: Union[tuple, dict, None] = None,
    commit_mode: str = 'once'
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
    if commit_mode == 'always':
        conn.commit()
    if temp_set_workmem is not None:
        print('Setting work_mem back to the previous value:', old_workmem)
        cur.execute('set work_mem = %s', (old_workmem,))
    if vacuum == 'always':
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
        conn,
        paths: Union[str, list, tuple],
        vacuum: str = 'once',
        temp_set_workmem: str = None,
        query_parameters: Union[tuple, dict, None] = None,
        commit_mode: str = 'once'
) -> None:
    """Method executes sql script from given file path(s)."""

    if len(paths) == 0:
        raise AttributeError('You need to specify at least one path for file with an sql script.')

    try:
        if type(paths) == str:
            _read_and_execute(conn, paths, vacuum, temp_set_workmem, query_parameters, commit_mode)
        elif type(paths) in (tuple, list):
            if type(paths[0]) in (tuple, list):
                for lst in paths:
                    for path in lst:
                        _read_and_execute(conn, path, vacuum, temp_set_workmem, query_parameters, commit_mode)
            else:
                for path in paths:
                    _read_and_execute(conn, path, vacuum, temp_set_workmem, query_parameters, commit_mode)
        else:
            raise AttributeError(f'Wrong arguments should be strings with paths or list of strings (paths): {paths}')
    except FileNotFoundError:
        print(datetime.now(timezone.utc).astimezone().isoformat(), '- Query file not found. Last transaction rolled back.')
        conn.rollback()
        raise

    if commit_mode in ('always', 'once'):
        conn.commit()
    if vacuum in ('always', 'once'):
        with conn.cursor() as cur:
            print('Vacuum analyze.')
            old_isolation_level = conn.isolation_level
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur.execute('VACUUM ANALYZE;')
            conn.set_isolation_level(old_isolation_level)


def full_process(dsn: str, starting: str = '000', force: bool = False) -> None:
    final_status: str = 'SUCCESS'
    ddls: list = []
    dmls: list = []
    # get paths of sql files
    # r=root, d=directories, f = files
    if starting == '000':
        for r, d, f in walk(ddl_path):
            for file in f:
                if file.endswith('.sql'):
                    ddls.append(join(r, file))
    for r, d, f in walk(dml_path):
        for file in f:
            if file.endswith('.sql') and file >= starting:
                dmls.append(join(r, file))
    # make sure dml files are sorted by names, ddl files should not require any specific order
    dmls = [x for x in sorted(dmls)]

    # execute sql scripts
    with pg.connect(dsn) as conn:
        cur = conn.cursor()
        cur.execute('SELECT in_progress FROM process_locks WHERE process_name = %s', ('prg_full_update',))
        full_update_in_progress = cur.fetchone()[0] if not force else False
        if not full_update_in_progress:
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- starting full update process.')
            cur.execute('UPDATE process_locks SET (in_progress, start_time, end_time) = (true, \'now\', null) ' +
                        'WHERE process_name = %s',
                        ('prg_full_update',))
            conn.commit()
            try:
                if len(ddls) > 0:
                    execute_scripts_from_files(conn=conn, vacuum='never', paths=ddls, commit_mode='once')
                execute_scripts_from_files(conn=conn, vacuum='once', paths=dmls, temp_set_workmem='2048MB', commit_mode='always')
            except FileNotFoundError:
                final_status = 'FAIL'
            cur.execute('UPDATE process_locks SET (in_progress, end_time, last_status) = (false, \'now\', %s) ' +
                        'WHERE process_name = %s',
                        (final_status, 'prg_full_update'))
            conn.commit()
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- finished full update process.')
        else:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  '- full update in progress already. Not starting another one.')


def partial_update(dsn: str, starting: str = '000') -> None:
    final_status: str = 'SUCCESS'
    sql_queries: list = []
    # get paths of sql files
    # r=root, d=directories, f = files
    for r, d, f in walk(partial_update_path):
        for file in f:
            if file.endswith('.sql') and file >= starting:
                sql_queries.append(join(r, file))
    sql_queries = [x for x in sorted(sql_queries)]
    with pg.connect(dsn) as conn:
        cur = conn.cursor()
        cur.execute('SELECT in_progress FROM process_locks WHERE process_name in (%s, %s)',
                    ('prg_full_update', 'prg_partial_update'))
        update_in_progress = [x[0] for x in cur.fetchall()]
        if not any(update_in_progress):
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- starting partial update process.')
            cur.execute('UPDATE process_locks SET (in_progress, start_time, end_time) = (true, \'now\', null) ' +
                        'WHERE process_name = %s',
                        ('prg_partial_update',))
            conn.commit()
            cur.execute('SELECT * FROM expired_tiles WHERE processed = false FOR UPDATE SKIP LOCKED;')
            for i, row in enumerate(cur.fetchall()):
                x, y, z = row[2], row[3], row[1]
                tile = m.Tile(x, y, z)
                bbox = to_merc(m.bounds(tile))
                bbox = {'xmin': bbox['west'], 'ymin': bbox['south'], 'xmax': bbox['east'], 'ymax': bbox['north']}
                try:
                    execute_scripts_from_files(conn=conn, vacuum='never', paths=sql_queries,
                                               query_parameters=bbox, commit_mode='off')
                except FileNotFoundError:
                    final_status = 'FAIL'
                    cur.execute(
                        'UPDATE expired_tiles SET processed = false ' +
                        'WHERE file_name = %s and z = %s and x = %s and y = %s;',
                        (row[0], row[1], row[2], row[3])
                    )
                    break
                cur.execute(
                    'UPDATE expired_tiles SET processed = true WHERE file_name = %s and z = %s and x = %s and y = %s;',
                    (row[0], row[1], row[2], row[3])
                )
                if i % 10 == 0:
                    conn.commit()
            cur.execute(
                'UPDATE process_locks SET (in_progress, end_time, last_status) = (false, \'now\', %s) WHERE process_name = %s',
                (final_status, 'prg_partial_update',))
            conn.commit()
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- finished partial update process.')
        else:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  '- update in progress skipping partial update.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', help='Launch full process', nargs='?', const=True)
    parser.add_argument('--update', help='Launch partial update process', nargs='?', const=True)
    parser.add_argument('--force', help='Ignore checking if another process is running. Applies to full process.', nargs='?', const=True)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL DB.', nargs=1)
    parser.add_argument('--starting', help='Start from this query (DML or Partial Update). Must match name exactly.', nargs=1)
    args = vars(parser.parse_args())

    dsn = args['dsn'][0]
    if 'full' in args and args.get('full'):
        if args.get('starting'):
            full_process(dsn, starting=args.get('starting')[0], force=args.get('force'))
        else:
            full_process(dsn, force=args.get('force'))
    elif 'update' in args and args.get('update'):
        if args.get('starting'):
            partial_update(dsn, args.get('starting')[0])
        else:
            partial_update(dsn)
