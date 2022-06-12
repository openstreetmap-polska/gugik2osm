import logging
import re
import zipfile
from base64 import b64decode
from io import BytesIO, TextIOWrapper, StringIO
from os.path import join, dirname, abspath
from typing import NamedTuple

from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from zeep import Client
from zeep.wsse.username import UsernameToken


class Configuration(NamedTuple):
    table: str
    api_method: str
    copy_command: str


logger = logging.getLogger()

wsdl_path = {
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

registriesConfiguration = {
    'terc': Configuration(
        table='teryt.terc',
        api_method='PobierzKatalogTERC',
        copy_command="COPY teryt.terc FROM stdin DELIMITER ';' CSV HEADER;",
    ),
    'simc': Configuration(
        table='teryt.simc',
        api_method='PobierzKatalogSIMC',
        copy_command="COPY teryt.simc FROM stdin DELIMITER ';' CSV HEADER;",
    ),
    'ulic': Configuration(
        table='teryt.ulic',
        api_method='PobierzKatalogULIC',
        copy_command="COPY teryt.ulic FROM stdin DELIMITER ';' CSV HEADER;",
    ),
    'wmrodz': Configuration(
        table='teryt.wmrodz',
        api_method='PobierzKatalogWMRODZ',
        copy_command="COPY teryt.wmrodz FROM stdin DELIMITER ';' CSV HEADER;",
    ),
}


def read_inmemory_zipfile(file: BytesIO) -> StringIO:
    logger.info('Reading zip file.')
    with zipfile.ZipFile(file, 'r') as zf:
        for filename in zf.namelist():
            if filename.endswith('.csv'):
                logger.info(f'Found CSV file inside: {filename}.')
                # using rstrip since postgres COPY doesn't handle trailing whitespace
                text = TextIOWrapper(zf.open(filename, 'r'), encoding='utf-8-sig', newline=None).read().rstrip()
                # CSVs are not encoded properly, we need to be careful with non-standard apostrophes
                # postgres COPY handles quotes inside string even if not properly escaped,
                # but they need to be a matching pair
                fixed_text = re.sub('["＂〃ˮײ᳓″״‶˶ʺ“”˝‟]', '"', text)
                return StringIO(fixed_text)
        raise Exception('Did not find CSV file inside ZIP.')


def load2pg(content: StringIO, sql: str, connection_name: str = "postgres_default") -> None:
    logger.info('Connecting to PostgreSQL.')
    conn = PostgresHook(postgres_conn_id=connection_name).get_conn()
    cur = conn.cursor()
    logger.info('Loading data.')
    cur.copy_expert(sql=sql, file=content)
    logger.info(cur.statusmessage)
    conn.commit()
    conn.close()
    logger.info('Connection closed.')


def get_data_from_teryt_api(api_method: str, state_date: str, connection_name: str = "teryt_api_prod") -> StringIO:
    conn = BaseHook.get_connection(connection_name)
    env, api_user, api_password = conn.host, conn.login, conn.password
    logger.info('Connecting to TERYT API.')
    client = Client(wsdl_path[env], wsse=UsernameToken(api_user, api_password))
    logger.info(f'Calling API method: {api_method}.')
    response = client.service[api_method](DataStanu=state_date)
    logger.info('Received response.')
    zip_file = BytesIO(b64decode(response['plik_zawartosc']))
    return read_inmemory_zipfile(zip_file)


def get_data_from_api_and_load_to_db(
    registry_name: str,
    state_date: str,
    teryt_connection_name: str = "teryt_api_prod",
    postgres_connection_name: str = "postgres_default",
) -> None:
    if registry_name not in registriesConfiguration:
        raise ValueError(f'Name: {registry_name} not recognized. Should be one of: {registriesConfiguration.keys()}.')
    conf: Configuration = registriesConfiguration[registry_name]
    content = get_data_from_teryt_api(
        api_method=conf.api_method,
        state_date=state_date,
        connection_name=teryt_connection_name,
    )
    load2pg(
        content=content,
        sql=conf.copy_command,
        connection_name=postgres_connection_name,
    )
