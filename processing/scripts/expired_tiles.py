import argparse
import os
import shutil
from datetime import datetime, timezone
from os.path import join
from os import listdir
import psycopg2 as pg


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


def insert_tiles_into_db(file_name: str, tiles: list, dsn: str) -> None:
    if len(tiles) > 0:
        with pg.connect(dsn) as conn:
            cur = conn.cursor()
            for tile in tiles:
                z, x, y = str(tile).split('/')
                z, x, y = int(z), int(x), int(y.rstrip())
                print(
                    datetime.now(timezone.utc).astimezone().isoformat(),
                    '- inserting row with values:',
                    (file_name, z, x, y)
                )
                cur.execute(
                    'INSERT INTO expired_tiles (file_name, z, x, y) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;',
                    (file_name, z, x, y)
                )
            conn.commit()


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
            dsn = f'host={PGHOSTADDR} port={PGPORT} dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD}'
        else:
            dsn = args['dsn']

        if args.get('all'):
            for tup in expired_tiles_from_all_todays_files(args['dir'][0]):
                insert_tiles_into_db(tup[0], tup[1], dsn)
        else:
            expt = expired_tiles_from_newest_file(args['dir'][0])
            if len(expt) > 0:
                file_name, tiles = expt
                insert_tiles_into_db(file_name, tiles, dsn)
            else:
                print(datetime.now(timezone.utc).astimezone().isoformat(), '- no expired tiles.')
