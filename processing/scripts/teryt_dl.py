import argparse
import os
import zipfile
from base64 import b64decode
from io import BytesIO, TextIOWrapper, StringIO
from os.path import join, dirname, abspath
from datetime import datetime, timedelta, timezone

from zeep import Client
from zeep.wsse.username import UsernameToken
import psycopg2 as pg

url = {
    'prod': join(dirname(abspath(__file__)), 'terytws1.wsdl'),
    'test': join(dirname(abspath(__file__)), 'terytws1test.wsdl')
}

sql_prepare_tables = '''
CREATE SCHEMA IF NOT EXISTS teryt;

DROP TABLE IF EXISTS teryt.terc;
CREATE TABLE teryt.terc (
  woj text,
  pow text,
  gmi text,
  rodz text,
  nazwa  text,
  nazdod text,
  stan_na text
);

DROP TABLE IF EXISTS teryt.simc;
CREATE TABLE teryt.simc (
  woj text,
  pow text,
  gmi text,
  rodz_gmi text,
  rm text,
  mz text,
  nazwa text,
  sym text,
  sympod text,
  stan_na text
);

DROP TABLE IF EXISTS teryt.ulic;
CREATE TABLE teryt.ulic (
  woj text,
  pow text,
  gmi text,
  rodz_gmi text,
  sym text,
  sym_ul text,
  cecha text,
  nazwa_1 text,
  nazwa_2 text,
  stan_na text
);

DROP TABLE IF EXISTS teryt.wmrodz;
CREATE TABLE teryt.wmrodz (
  rm text,
  nazwa_rm text,
  stan_na text
);
'''

teryt = {
    'terc': {
        'table': 'teryt.terc',
        'api_method': 'PobierzKatalogTERC',
        'copy': "COPY teryt.terc FROM stdin DELIMITER ';' CSV HEADER;"
    },
    'simc': {
        'table': 'teryt.simc',
        'api_method': 'PobierzKatalogSIMC',
        'copy': "COPY teryt.simc FROM stdin DELIMITER ';' CSV HEADER;"
    },
    'ulic': {
        'table': 'teryt.ulic',
        'api_method': 'PobierzKatalogULIC',
        'copy': "COPY teryt.ulic FROM stdin DELIMITER ';' CSV HEADER;"
    },
    'wmrodz': {
        'table': 'teryt.wmrodz',
        'api_method': 'PobierzKatalogWMRODZ',
        'copy': "COPY teryt.wmrodz FROM stdin DELIMITER ';' CSV HEADER;"
    }
}


def readfile(f: BytesIO) -> StringIO:
    with zipfile.ZipFile(f, 'r') as zf:
        for filename in zf.namelist():
            if filename.endswith('.csv'):
                return StringIO(TextIOWrapper(zf.open(filename, 'r'), encoding='utf-8-sig', newline=None).read().rstrip())


def load2pg(conn, file: StringIO, key: str, prepare_tables: bool = False) -> None:
    cur = conn.cursor()
    if prepare_tables:
        cur.execute(sql_prepare_tables)
    cur.copy_expert(sql=teryt[key]['copy'], file=file)
    conn.commit()


def main(env: str, dsn: str, api_user: str, api_password: str, date: str = None) -> None:
    date = date if date else datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    final_status: str = 'SUCCESS'
    with pg.connect(dsn) as conn:
        cur = conn.cursor()
        cur.execute('SELECT in_progress FROM process_locks WHERE process_name = %s', ('teryt_update',))
        teryt_update_in_progress = cur.fetchone()[0]
        if not teryt_update_in_progress:
            print(datetime.now(timezone.utc).astimezone().isoformat(), '- starting TERYT update process.')
            cur.execute('UPDATE process_locks SET (in_progress, start_time, end_time) = (true, \'now\', null) ' +
                        'WHERE process_name = %s',
                        ('teryt_update',))
            conn.commit()
            try:
                for i, key in enumerate(teryt.keys()):
                    client = Client(url[env], wsse=UsernameToken(api_user, api_password))
                    r = client.service[teryt[key]['api_method']](DataStanu=date)
                    f = BytesIO(b64decode(r['plik_zawartosc']))
                    load2pg(conn, readfile(f), key, prepare_tables=i == 0)
            except Exception as e:
                conn.rollback()
                final_status = 'FAIL'
                print(datetime.now(timezone.utc).astimezone().isoformat(), '- error during TERYT update process.')
                print(e)
                raise e
            finally:
                cur.execute(
                    'UPDATE process_locks SET (in_progress, end_time, last_status) = (false, \'now\', %s) ' +
                    'WHERE process_name = %s',
                    (final_status, 'teryt_update',))
                conn.commit()
                print(datetime.now(timezone.utc).astimezone().isoformat(), '- finished TERYT update process.')
                conn.close()
        else:
            print(datetime.now(timezone.utc).astimezone().isoformat(),
                  '- TERYT update in progress already. Not starting another one.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_env', help='TERYT API environment.', nargs=1, choices=['prod', 'test'])
    parser.add_argument('--api_user', help='TERYT API user.', nargs='?')
    parser.add_argument('--api_password', help='TERYT API password.', nargs='?')
    parser.add_argument('--dsn', help='Connection string for PostgreSQL DB.', nargs='?')
    parser.add_argument('--dotenv', help='Path to .env file with credentials for PostgreSQL DB.', nargs='?')
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
        api_user = os.environ['TERYTUSER']
        api_password = os.environ['TERYTPASSWORD']
    else:
        dsn = args['dsn']
        api_user = args['api_user']
        api_password = args['api_password']
    api_env = args['api_env']

    main(api_env, dsn, api_user, api_password)
