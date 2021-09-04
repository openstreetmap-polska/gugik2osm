# definition of tables in ../sql/ddl/changesets_processing.sql

import argparse
import os
import re
from glob import glob
import json
from dataclasses import dataclass
from typing import List, Generator

import psycopg2
import psycopg2.extras
from lxml import etree


@dataclass
class BBox:
    ymin: float
    xmin: float
    ymax: float
    xmax: float

    def intersects(self, bbox) -> bool:
        if any((
            bbox.xmin > self.xmax,
            bbox.xmax < self.xmin,
            bbox.ymin > self.ymax,
            bbox.ymax < self.ymin
        )):
            return False
        else:
            return True

    @property
    def as_wkt(self) -> str:
        return (f'Polygon (({self.xmin} {self.ymin}, {self.xmax} {self.ymin}, {self.xmax} {self.ymax}, '
                +
                f'{self.xmin} {self.ymax}, {self.xmin} {self.ymin}))')


BBOX_POLAND = BBox(49.002, 14.0696, 55.0361, 24.1458)


def relative_file_path(file_path: str) -> str:
    fn = re.search(
        r'[\\/]{1,2}(\d{3}[\\/]{1,2}\d{3}[\\/]{1,2}\d{3}\.osm\.gz)',
        file_path,
        re.IGNORECASE
    )
    if fn:
        return fn.group(1).replace('\\', '/').replace('//', '/')
    else:
        return os.path.basename(file_path)


def xml_iterator(context: etree.iterparse) -> etree.Element:
    """Memory efficient XML iterator."""

    for _event, elem in context:
        yield elem
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def parsed_changesets(
        file_path: str,
        only_closed: bool = True,
        restrict_to_bbox: BBox = None,
        allow_no_coordinates: bool = False
) -> Generator[dict, None, None]:

    fn = relative_file_path(file_path)

    tree = etree.parse(file_path)
    root = tree.getroot()

    for el in root:
        if only_closed and el.get('open') == 'true':
            continue
        if restrict_to_bbox is not None:
            min_lat, min_lon = el.get('min_lat'), el.get('min_lon')
            max_lat, max_lon = el.get('max_lat'), el.get('max_lon')
            if all((min_lat, min_lon, max_lat, max_lon)):
                min_lat, min_lon = float(min_lat), float(min_lon)
                max_lat, max_lon = float(max_lat), float(max_lon)
                changeset_bbox = BBox(min_lat, min_lon, max_lat, max_lon)
                if not restrict_to_bbox.intersects(changeset_bbox):
                    continue
            else:
                if not allow_no_coordinates:
                    continue

        min_lat = float(el.get('min_lat')) if el.get('min_lat') else None
        min_lon = float(el.get('min_lon')) if el.get('min_lon') else None
        max_lat = float(el.get('max_lat')) if el.get('max_lat') else None
        max_lon = float(el.get('max_lon')) if el.get('max_lon') else None
        yield {
            'file_path': fn,
            'changeset_id': int(el.get('id')),
            'created_at': el.get('created_at'),
            'closed_at': el.get('closed_at'),
            'open': el.get('open') and el.get('open') == 'true',
            'num_changes': int(el.get('num_changes')) if el.get('num_changes') is not None else None,
            'osm_user': el.get('user'),
            'uid': int(el.get('uid')) if el.get('uid') is not None else None,
            'comments_count': int(el.get('comments_count')) if el.get('comments_count') is not None else None,
            'tags': json.dumps({
                x.get('k'): x.get('v')
                for x in el.getchildren()
                if x.tag == 'tag'
            }),
            'bbox': BBox(min_lat, min_lon, max_lat, max_lon).as_wkt if min_lat is not None else None,
        }


def list_files(directory: str, pattern: str = '**/*.osm.gz') -> List[str]:
    files = glob(os.path.join(directory, pattern), recursive=True)
    return list(sorted(files))


def list_files_not_loaded_yet(directory: str, pg_dsn: str, pattern: str = '**/*.osm.gz') -> List[str]:
    files = list_files(directory, pattern)
    connection = psycopg2.connect(pg_dsn)
    try:
        cur = connection.cursor()
        cur.execute('SELECT file_path FROM changesets_processing.processed_files')
        loaded_files = [f[0] for f in cur.fetchall()]
    except psycopg2.Error as err:
        print('There was a problem getting list of processed files from DB. Error:', err)
        raise err
    finally:
        connection.close()
    loaded_files = set(loaded_files)
    files_not_loaded_yet = [f for f in files if relative_file_path(f) not in loaded_files]
    return list(sorted(files_not_loaded_yet))


def load_data_from_files(
        connection,
        list_of_filepaths: List[str],
        allow_no_coordinates: bool = False,
        restrict_to_bbox: BBox = None,
        commit_every_n_files: int = 10
) -> None:
    cursor = connection.cursor()
    fill = len(str(len(list_of_filepaths)))
    total_num = len(list_of_filepaths)
    for idx, file_path in enumerate(list_of_filepaths):
        print(f'{str(idx+1).zfill(fill)}/{total_num} - Processing file: {file_path} .')
        if not os.path.isfile(file_path):
            print('Not a file. Skipping.')
            continue
        if os.stat(file_path).st_size == 0:
            print('File has size of 0 bytes. Skipping.')
            continue
        psycopg2.extras.execute_values(
            cursor,
            '''INSERT INTO changesets_processing.changesets (
                file_path,
                changeset_id,
                created_at,
                closed_at,
                open,
                num_changes,
                osm_user,
                uid,
                min_lat,
                min_lon,
                max_lat,
                max_lon,
                comments_count,
                tags,
                bbox
            ) VALUES %s ''',
            parsed_changesets(
                file_path,
                only_closed=True,
                restrict_to_bbox=restrict_to_bbox,
                allow_no_coordinates=allow_no_coordinates
            ),
            page_size=1000,
            template='''(
                %(file_path)s,
                %(changeset_id)s,
                %(created_at)s,
                %(closed_at)s,
                %(open)s,
                %(num_changes)s,
                %(osm_user)s,
                %(uid)s,
                %(min_lat)s,
                %(min_lon)s,
                %(max_lat)s,
                %(max_lon)s,
                %(comments_count)s,
                %(tags)s,
                %(bbox)s
            )'''
        )
        cursor.execute(
            'INSERT INTO changesets_processing.processed_files VALUES ( %s )',
            (relative_file_path(file_path),)
        )
        if (idx + 1) % commit_every_n_files == 0:
            connection.commit()
            print('Commit.')

    connection.commit()
    print('Commit.')
    cursor.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--changesets-dir', help='Path to the directory where files are to be placed.', nargs=1)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL database with data about counties loaded by teryt_dl script.', nargs='?')
    parser.add_argument('--dotenv', help='Path to .env file with credentials for PostgreSQL DB.', nargs='?')
    parser.add_argument('--allow-no-coordinates', help='Allow loading changesets that do not have coordinates.', nargs='?', const=True)
    parser.add_argument(
        '--restrict-to-bbox',
        help=('Restrict changests to those that intersects given bbox. Provide either comma separated list of ' +
              'coordiantes xmin,ymin,xmax,ymax or write poland for Poland\'s bbox.'),
        nargs='?'
    )
    parser.add_argument('--process-not-loaded-yet', help='Only process files that have not been processed yet.', nargs='?', const=True)
    args = vars(parser.parse_args())

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

    changesets_dir = args['changesets_dir'][0]
    allow_no_coords = True if args.get('allow_no_coordinates') else False
    process_not_loaded_yet = True if args.get('process_not_loaded_yet') else False
    if args.get('restrict-to-bbox'):
        if args.get('restrict-to-bbox').lower() == 'poland':
            data_bbox = BBOX_POLAND
        else:
            data_bbox = BBox(*list(map(float, args.get('restrict-to-bbox').split(','))))
    else:
        data_bbox = None

    if process_not_loaded_yet:
        file_paths = list_files_not_loaded_yet(changesets_dir, dsn)
    else:
        file_paths = list_files(changesets_dir)

    print(f'Number of files to process: {len(file_paths)}.')

    conn = psycopg2.connect(dsn)
    try:
        load_data_from_files(
            conn,
            list_of_filepaths=file_paths,
            allow_no_coordinates=allow_no_coords,
            restrict_to_bbox=data_bbox,
            commit_every_n_files=100
        )
    except psycopg2.Error as e:
        print('There was a problem getting list of processed files from DB.')
        raise e
    finally:
        conn.close()

    print('Done.')
