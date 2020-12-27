import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.error
import shutil
from os import path
from time import sleep
from typing import Tuple

BASE_URL = 'https://opendata.geoportal.gov.pl/bdot10k/{woj}/{pow}_GML.zip'


def download_file(url: str, file_path: str, _try_number: int = 1) -> None:
    print(datetime.now(timezone.utc).astimezone().isoformat(), '- downloading:', file_path, 'from:', url)
    try:
        with urllib.request.urlopen(url) as response:
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as e:
        if _try_number > 3:
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- There was a problem downloading:', file_path,
                  'from:', url,
                  '- Status code:', e.code, '-', e)
            raise e
        else:
            sleep(2)
            download_file(url, file_path, _try_number=_try_number + 1)
    except ConnectionResetError as e2:
        if _try_number > 3:
            raise e2
        else:
            sleep(2)
            download_file(url, file_path, _try_number=_try_number+1)


def prepare_url_and_filepath(teryt_code: str) -> Tuple[str, str]:
    teryt_code = args.get('only')
    fn = 'BDOT10k_{0}.zip'.format(teryt_code)
    url = BASE_URL.format(woj=teryt_code[:2], pow=teryt_code)
    file_path = path.join(args['output_dir'][0], fn)
    return url, file_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', help='File path to the directory where files are to be placed.', nargs=1)
    parser.add_argument('--only', help='Download only this county\'s file. (provide 4 digit TERYT code)', nargs='?')
    parser.add_argument('--dsn', help='Connection string for PostgreSQL database with data about counties loaded by teryt_dl script.', nargs='?')
    args = vars(parser.parse_args())

    if args.get('only'):
        url, file_path = prepare_url_and_filepath(args.get('only'))
        download_file(url, file_path)
    else:
        import psycopg2 as pg

        query = 'select woj || pow as kod_teryt from teryt.terc where pow is not null and gmi is null'

        with pg.connect(args.get('dsn')) as conn:
            cur = conn.cursor()
            try:
                cur.execute(query)
            except pg.Error as e:
                print(datetime.now(timezone.utc).astimezone().isoformat(), '- There was a problem executing query.', e)

            for tup in cur.fetchall():
                url, file_path = prepare_url_and_filepath(tup[0])
                download_file(url, file_path)
