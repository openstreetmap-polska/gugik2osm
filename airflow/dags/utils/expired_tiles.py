import logging
import shutil
from datetime import datetime
from os.path import join
from os import listdir
from typing import List, Tuple, Generator

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger()


def expired_tiles_from_n_newest_files(base_dir: str, n: int = 3) -> Generator[Tuple[str, List[str]], None, None]:

    sorted_dirs = sorted(listdir(base_dir), reverse=True)
    if len(sorted_dirs) == 0:
        return tuple()
    newest_dir = sorted_dirs[0]

    path = join(base_dir, newest_dir)
    files_with_tiles = [x for x in listdir(path) if x.endswith('.tiles')]

    for file_path in sorted(files_with_tiles, reverse=True)[:n]:
        with open(join(path, file_path), 'r') as f:
            lines = f.readlines()
            yield file_path, lines


def expired_tiles_from_all_todays_files(base_dir: str) -> Generator[Tuple[str, List[str]], None, None]:
    temp = datetime.now()
    today = str(temp.year) + str(temp.month).zfill(2) + str(temp.day).zfill(2)

    path = join(base_dir, today)
    files_with_tiles = [x for x in listdir(path) if x.endswith('.tiles')]

    for file in files_with_tiles:
        with open(join(path, file), 'r') as f:
            lines = f.readlines()
            yield file, lines


def insert_tiles_into_db(
    file_name: str,
    list_of_tiles: List[str],
    postgres_connection_name: str = "postgres_default",
) -> None:

    temp_table_ddl = """
        CREATE TEMPORARY TABLE temp_expired_tiles (
            file_name text,
            z int,
            x int,
            y int
        )
    """.strip()
    insert_tiles_dml = """
        with
        tiles_to_insert as (
            select file_name, z, x, y
            from temp_expired_tiles
            left join expired_tiles as existing using(file_name, z, x, y)
            where 1=1
                and ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_TileEnvelope(z, x, y)
                and existing.file_name is null
        )
        insert into expired_tiles (file_name, z, x, y)
            select file_name, z, x, y
            from tiles_to_insert
        on conflict do nothing
    """.strip()

    logger.info(f"Inserting tiles from: {file_name}.")
    if len(list_of_tiles) > 0:
        conn = PostgresHook(postgres_conn_id=postgres_connection_name).get_conn()
        cur = conn.cursor()
        logger.info(f"Number of tiles to insert: {len(list_of_tiles)}")
        try:
            cur.execute(temp_table_ddl)
            values = [
                cur.mogrify("(%s,%s,%s,%s)", tup).decode('utf8')
                for tup in _prepare_tuple_to_insert(file_name, list_of_tiles)
            ]
            insert_query = "INSERT INTO temp_expired_tiles(file_name, z, x, y) VALUES " + ",".join(values)
            cur.execute(insert_query)
            logger.info(cur.statusmessage)
            logger.info(cur.rowcount)
            cur.execute(insert_tiles_dml)
            logger.info(cur.statusmessage)
            logger.info(cur.rowcount)
            for notice in conn.notices:
                logger.info(str(notice).strip())
            conn.commit()
            conn.close()
            logger.info("Insert finished. Connection closed.")
        except:
            logger.error("Error while trying to insert expired tiles to db.", exc_info=True)
        finally:
            conn.close()
    else:
        logger.info("Number of tiles to insert is 0. Nothing to do.")


def _prepare_tuple_to_insert(
    file_name: str,
    list_of_tiles: List[str],
) -> Generator[Tuple[str, int, int, int], None, None]:

    for tile in list_of_tiles:
        z, x, y = str(tile).strip().split('/')
        z, x, y = int(z), int(x), int(y)
        yield file_name, z, x, y


def remove_folder_older_than_today(base_dir: str) -> None:
    temp = datetime.now()
    today = str(temp.year) + str(temp.month).zfill(2) + str(temp.day).zfill(2)
    for p in [x for x in listdir(base_dir) if x < today]:
        path = join(base_dir, p)
        logger.info(f"Removing: {path}")
        shutil.rmtree(path)


def insert_tiles_from_n_newest_files(folder: str, n: int = 3) -> None:
    for file_name, list_of_tiles in expired_tiles_from_n_newest_files(base_dir=folder, n=n):
        insert_tiles_into_db(file_name, list_of_tiles)
