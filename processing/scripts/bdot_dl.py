import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.error
import shutil
from os import path


BASE_URL = 'https://opendata.geoportal.gov.pl/bdot10k/{woj}/{pow}_GML.zip'


def download_file(url: str, file_path: str):
    print(datetime.now(timezone.utc).astimezone().isoformat(), '- downloading:', fn, 'from:', url)
    try:
        with urllib.request.urlopen(url) as response:
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as e:
        print(datetime.now(timezone.utc).astimezone().isoformat(), '- There was a problem downloading:', fn,
              'from:', url,
              '- Status code:', e.code, '-', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', help='File path to the directory where files are to be placed.', nargs=1)
    parser.add_argument('--only', help='Download only this county\'s file. (provide 4 digit TERYT code)', nargs='?')
    parser.add_argument('--dsn', help='Connection string for PostgreSQL database with data about counties loaded by teryt_dl script.', nargs='?')
    args = vars(parser.parse_args())

    if args.get('only'):
        teryt_code = args.get('only')
        fn = 'BDOT10k_{0}.zip'.format(teryt_code)
        url = BASE_URL.format(woj=teryt_code[:2], pow=teryt_code)
        file_path = path.join(args['output_dir'][0], fn)
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
                teryt_code = tup[0]
                fn = 'BDOT10k_{0}.zip'.format(teryt_code)
                url = BASE_URL + teryt_code
                file_path = path.join(args['output_dir'][0], fn)
                download_file(url, file_path)
