import argparse
import os
import shutil
from datetime import datetime, timezone
from os.path import join
from os import listdir
from typing import List

import psycopg2 as pg
import psycopg2.extras


def expired_tiles_from_newest_file(base_dir: str) -> tuple:

    sorted_dirs = sorted(listdir(base_dir), reverse=True)
    if len(sorted_dirs) == 0:
        return tuple()
    newest_dir = sorted_dirs[0]

    path = join(base_dir, newest_dir)
    files_with_tiles = [x for x in listdir(path) if x.endswith('.tiles')]

    if len(files_with_tiles) == 0:
        return tuple()

    newest_file = sorted(files_with_tiles, reverse=True)[0]
    with open(join(path, newest_file), 'r') as f:
        lines = f.readlines()
    return newest_file, lines


def expired_tiles_from_all_todays_files(base_dir: str) -> list:
    temp = datetime.now()
    today = str(temp.year) + str(temp.month).zfill(2) + str(temp.day).zfill(2)

    path = join(base_dir, today)
    files_with_tiles = [x for x in listdir(path) if x.endswith('.tiles')]

    results = []
    for file in files_with_tiles:
        with open(join(path, file), 'r') as f:
            lines = f.readlines()
        results.append((file, lines))
    return results


def insert_tiles_into_db(file_name: str, list_of_tiles: List[str], dsn: str) -> None:
    query = '''
        with
        tiles (file_name, z, x, y) as (
            VALUES %s
        ),
        tiles_to_insert as (
            select *
            from tiles
            where 1=1
                and ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_TileEnvelope(z, x, y)
        )
        insert into expired_tiles  
            select *
            from tiles_to_insert
        on conflict do nothing
    '''
    if len(list_of_tiles) > 0:
        print(datetime.now(timezone.utc).astimezone().isoformat(), f'Tiles to insert: {len(list_of_tiles)}.')
        conn = pg.connect(dsn)
        try:
            cursor = conn.cursor()
            pg.extras.execute_values(cursor, query, _prepare_tuple_to_insert(file_name, list_of_tiles), page_size=1000)
            for notice in conn.notices:
                print(str(notice).strip())
            conn.commit()
        except pg.Error as e:
            print('Error inserting expired tiles:', e)
        finally:
            conn.close()
        print(datetime.now(timezone.utc).astimezone().isoformat(), 'Done.')


def _prepare_tuple_to_insert(file_name: str, list_of_tiles: List[str]):
    for tile in list_of_tiles:
        z, x, y = str(tile).split('/')
        z, x, y = int(z), int(x), int(y.rstrip())
        yield file_name, z, x, y


def remove_folder_older_than_today(base_dir: str) -> None:
    temp = datetime.now()
    today = str(temp.year) + str(temp.month).zfill(2) + str(temp.day).zfill(2)
    for p in [x for x in listdir(base_dir) if x < today]:
        path = join(base_dir, p)
        print(datetime.now(timezone.utc).astimezone().isoformat(), '- removing:', path)
        shutil.rmtree(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--remove-old-folders', help='Remove folders older than today', nargs='?', const=True)
    parser.add_argument('--insert-exp-tiles', help='Read and insert into db the expired tiles', nargs='?', const=True)
    parser.add_argument('--all', help='Read all todays tiles files (flag to be used in conjunction with insert)', nargs='?', const=True)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL DB.', nargs='?')
    parser.add_argument('--dotenv', help='Path to .env file with credentials for PostgreSQL DB.', nargs='?')
    parser.add_argument('--dir', help='Base directory where folders/files with expired tiles are stored', nargs=1)
    args = vars(parser.parse_args())

    if args.get('remove_old_folders'):
        remove_folder_older_than_today(args['dir'][0])
    elif args.get('insert_exp_tiles'):
        if args.get('dotenv'):
            from dotenv import load_dotenv
            dotenv_path = args['dotenv']
            load_dotenv(dotenv_path, verbose=True)
            PGHOSTADDR = os.environ['PGHOSTADDR']
            PGPORT = os.environ['PGPORT']
            PGDATABASE = os.environ['PGDATABASE']
            PGUSER = os.environ['PGUSER']
            PGPASSWORD = os.environ['PGPASSWORD']
            pg_dsn = f'host={PGHOSTADDR} port={PGPORT} dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD}'
        else:
            pg_dsn = args['dsn']

        if args.get('all'):
            for tup in expired_tiles_from_all_todays_files(args['dir'][0]):
                insert_tiles_into_db(tup[0], tup[1], pg_dsn)
        else:
            expt = expired_tiles_from_newest_file(args['dir'][0])
            if len(expt) > 0:
                insert_tiles_into_db(*expt, pg_dsn)
            else:
                print(datetime.now(timezone.utc).astimezone().isoformat(), '- no expired tiles.')
