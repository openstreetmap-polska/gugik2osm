"""Based on:
https://www.ibm.com/developerworks/xml/library/x-hiperfparse/
"""
import zipfile
from os.path import getsize, join
import re
from datetime import datetime
from typing import List, Union, Dict, Set, Tuple, TextIO, BinaryIO
from collections import OrderedDict
import argparse

from lxml import etree


def incremented_name(name: str) -> str:
    """Helper function. Returns name with the next number.
       Examples:
        test -> test_01
        test_01 -> test_02
        test_02 -> test_03
        etc.
    """
    digits: str = ''
    for c in reversed(name):
        if c.isdigit():
            digits = c + digits
        else:
            break
    if len(digits) > 0:
        no: int = int(digits)
        return name[:-1 * len(digits)] + str(no + 1).rjust(2, '0')
    else:
        return name + '_01'


def fix_typo(name: str) -> str:
    """Helper function. Fix typo in one of the tags"""
    return 'jednostkaAdministracyjna' if name == 'jednostkaAdmnistracyjna' else name


class Namespaces:

    def __init__(self):
        # initial namespaces
        # XLINK is an exception being namespace with a tag already since it's pretty much the only use of it anyway
        self.XLINK: str = r'{http://www.w3.org/1999/xlink}href'
        self.NS_PRG: str = r'urn:gugik:specyfikacje:gmlas:panstwowyRejestrGranicAdresy:1.0'
        self.NS_GML: str = r'http://www.opengis.net/gml/3.2'
        self.NS_XSI: str = r'http://www.w3.org/2001/XMLSchema-instance'
        self.NS_BT: str = r'urn:gugik:specyfikacje:gmlas:modelPodstawowy:1.0'
        self.NS_MUA: str = r'urn:gugik:specyfikacje:gmlas:ewidencjaMiejscowosciUlicAdresow:1.0'

    def update_from_file(self, file_obj: Union[TextIO, BinaryIO]) -> None:
        """Updates namespaces in the class from xml file by looking at the file's first 15 lines."""
        for _ in range(15):
            line = file_obj.readline() if type(file_obj.readline()) == str else file_obj.readline().decode('UTF-8')
            re_ns_prg = re.search(
                r'xmlns:prg-ad="(urn:gugik:specyfikacje:gmlas:panstwowyRejestrGranicAdresy:\d\.\d)"',
                line,
                flags=re.RegexFlag.IGNORECASE
            )
            re_ns_gml = re.search(
                r'xmlns:gml="(http://www\.opengis\.net/gml/\d\.\d)"',
                line,
                flags=re.RegexFlag.IGNORECASE
            )
            re_ns_bt = re.search(
                r'(urn:gugik:specyfikacje:gmlas:modelPodstawowy:\d\.\d)',
                line,
                flags=re.RegexFlag.IGNORECASE
            )
            re_ns_mua = re.search(
                r'(urn:gugik:specyfikacje:gmlas:ewidencjaMiejscowosciUlicAdresow:\d\.\d)',
                line,
                flags=re.RegexFlag.IGNORECASE
            )
            if re_ns_prg:
                self.NS_PRG = re_ns_prg.group(1)
            if re_ns_gml:
                self.NS_GML = re_ns_gml.group(1)
            if re_ns_bt:
                self.NS_BT = re_ns_bt.group(1)
            if re_ns_mua:
                self.NS_MUA = re_ns_mua.group(1)


class Tags:

    def __init__(self, namespaces: Namespaces):
        self.JA: str = '{' + namespaces.NS_PRG + '}PRG_JednostkaAdministracyjnaNazwa'
        self.MSC: str = '{' + namespaces.NS_PRG + '}PRG_MiejscowoscNazwa'
        self.UL: str = '{' + namespaces.NS_PRG + '}PRG_UlicaNazwa'
        self.PA: str = '{' + namespaces.NS_PRG + '}PRG_PunktAdresowy'
        self.no_ns: dict = {
            self.JA: 'PRG_JednostkaAdministracyjnaNazwa',
            self.MSC: 'PRG_MiejscowoscNazwa',
            self.UL: 'PRG_UlicaNazwa',
            self.PA: 'PRG_PunktAdresowy'
        }
        self.with_ns: dict = {
            'PRG_JednostkaAdministracyjnaNazwa': self.JA,
            'PRG_MiejscowoscNazwa': self.MSC,
            'PRG_UlicaNazwa': self.UL,
            'PRG_PunktAdresowy': self.PA
        }
        self.no_ns2short: dict = {
            'PRG_JednostkaAdministracyjnaNazwa': 'JA',
            'PRG_MiejscowoscNazwa': 'MS',
            'PRG_UlicaNazwa': 'UL',
            'PRG_PunktAdresowy': 'PA'
        }

    def list(self, ja: bool = True, msc: bool = True, ul: bool = True, pa: bool = True) -> Set[str]:
        result = set()
        if ja:
            result.add(self.JA)
        if msc:
            result.add(self.MSC)
        if ul:
            result.add(self.UL)
        if pa:
            result.add(self.PA)
        if len(result) == 0:
            raise AttributeError('You can\'t give all parameters as false. At least one of them ought to be true.')
        return result


class Fields:

    def __init__(self, tags: Tags, only_basic_fields: bool = False):
        self.Tags: Tags = tags
        self.JA: OrderedDict[str, None] = OrderedDict()
        self.MSC: OrderedDict[str, None] = OrderedDict()
        self.UL: OrderedDict[str, None] = OrderedDict()
        self.PA: OrderedDict[str, None] = OrderedDict()
        self.set_default_fields()
        if only_basic_fields:
            self.set_only_basic_fields()
        else:
            self.set_default_fields()
        self.tag: Dict[str, OrderedDict[str, None]] = {
            self.Tags.JA: self.JA,
            self.Tags.MSC: self.MSC,
            self.Tags.UL: self.UL,
            self.Tags.PA: self.PA
        }

    def set_default_fields(self):
        self.JA = OrderedDict.fromkeys([
            'gmlid',
            'identifier',
            'lokalnyId',
            'przestrzenNazw',
            'wersjaId',
            'poczatekWersjiObiektu',
            'koniecWersjiObiektu',
            'waznyOd',
            'waznyDo',
            'nazwa',
            'idTERYT',
            'poziom',
            'jednostkaPodzialuTeryt'
        ])
        self.MSC = OrderedDict.fromkeys([
            'gmlid',
            'identifier',
            'lokalnyId',
            'przestrzenNazw',
            'wersjaId',
            'poczatekWersjiObiektu',
            'koniecWersjiObiektu',
            'waznyOd',
            'waznyDo',
            'nazwa',
            'idTERYT',
            'geometry',
            'miejscowosc'
        ])
        self.UL = OrderedDict.fromkeys([
            'gmlid',
            'identifier',
            'lokalnyId',
            'przestrzenNazw',
            'wersjaId',
            'poczatekWersjiObiektu',
            'koniecWersjiObiektu',
            'waznyOd',
            'waznyDo',
            'nazwaGlownaCzesc',
            'idTERYT',
            'geometry',
            'ulica'
        ])
        self.PA = OrderedDict.fromkeys([
            'gmlid',
            'identifier',
            'lokalnyId',
            'przestrzenNazw',
            'wersjaId',
            'poczatekWersjiObiektu',
            'koniecWersjiObiektu',
            'waznyOd',
            'waznyDo',
            'jednostkaAdministracyjna',
            'jednostkaAdministracyjna_01',
            'jednostkaAdministracyjna_02',
            'jednostkaAdministracyjna_03',
            'miejscowosc',
            'czescMiejscowosci',
            'ulica',
            'numerPorzadkowy',
            'kodPocztowy',
            'status',
            'geometry',
            'komponent',
            'komponent_01',
            'komponent_02',
            'komponent_03',
            'komponent_04',
            'komponent_05',
            'komponent_06',
            'obiektEMUiA'
        ])

    def set_only_basic_fields(self):
        self.set_default_fields()
        fields_to_remove = [
            'gmlid',
            'identifier',
            'przestrzenNazw',
            'wersjaId',
            'poczatekWersjiObiektu',
            'koniecWersjiObiektu',
            'waznyOd',
            'waznyDo'
        ]
        pa_fields_to_remove = [
            'komponent',
            'komponent_01',
            'komponent_02',
            'komponent_03',
            'komponent_04',
            'komponent_05',
            'komponent_06',
            'obiektEMUiA'
        ]
        for key in fields_to_remove:
            del self.JA[key]
            del self.MSC[key]
            del self.UL[key]
            del self.PA[key]
        for key in pa_fields_to_remove:
            del self.PA[key]

    def remove_fields(self, fields: List[str]) -> None:
        for key in fields:
            if key in self.JA:
                del self.JA[key]
            if key in self.MSC:
                del self.MSC[key]
            if key in self.UL:
                del self.UL[key]
            if key in self.PA:
                del self.PA[key]


class XML:

    def __init__(self, namespaces: Namespaces, tags: Tags, fields: Fields):
        self.NS: Namespaces = namespaces
        self.geometry_names: Set[str] = {'pozycja', 'geometria'}
        self.Tags: Tags = tags
        self.Fields: Fields = fields

    @staticmethod
    def me_xml_iterator(context: etree.iterparse) -> etree.Element:
        """Memory efficient XML iterator."""

        for _event, elem in context:
            yield elem
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

    def parse_element(self, el: etree.Element) -> Tuple[str, Dict[str, str]]:
        """Function that parses an element.
        Gets element 'gmlid' then recursively calls helper function for every value in an element."""

        parsed = self._parse_element_helper(
            el,
            (
                el.tag,
                {'gmlid': el.get('{' + self.NS.NS_GML + '}id')}
            )
        )
        return parsed

    def _parse_element_helper(
            self,
            el: etree.Element,
            carryover_values: Tuple[str, Dict[str, Union[str, None]]]
    ) -> Tuple[str, Dict[str, str]]:
        """Method called recursively to parse all element's values."""

        typ, result = carryover_values
        for x in el:
            # remove namespace from tag
            if x.prefix:
                x.tag = etree.QName(x).localname
            name = fix_typo(x.tag)

            # if no children and fields in the list of fields we want the values of
            # add data to dictionary
            if len(list(x)) == 0 and name in self.Fields.tag[typ]:
                # some tags appear multiple times with different values
                # but not attribute to make them distinct
                # so if we already have a key present
                # create new key with appended 2 digit number
                # if tag has empty text but contains xlink xref attribute
                # then take that as a value
                if name in result:
                    last_name = sorted([x for x in result.keys() if str(x).startswith(name)], reverse=True)[0]
                    name = incremented_name(last_name)
                # if value or href link start with url 'http://geoportal.gov.pl/PZGIK/dane/',
                # remove it as it is not necessary
                if x.text and x.text.startswith('http://geoportal.gov.pl'):
                    val = str(x.text)[35:]
                elif x.text is None and x.get(self.NS.XLINK) and x.get(self.NS.XLINK).startswith('http://geoportal.gov.pl'):
                    val = str(x.get(self.NS.XLINK))[35:]
                else:
                    val = x.text
                result[name] = x.get(self.NS.XLINK) if val is None and x.get(self.NS.XLINK) else val
            # if geometry
            # we want to preserve geometry string in GML format to parse it later
            elif x.tag in self.geometry_names:
                if len(x.getchildren()) > 0:
                    # create a new xml node called geometry and add our gml geometry as a child
                    # also get rid of namespaces that are not used
                    gml = etree.Element('geometry', nsmap={'gml': self.NS.NS_GML})
                    gml.insert(0, x.getchildren()[0])
                    result['geometry'] = etree.tostring(gml, pretty_print=False).decode()
                else:  # null geometry
                    result['geometry'] = None
            # if nested
            # go into the element
            # we want to flatten the document into a table
            else:
                self._parse_element_helper(x, (typ, result))
        return typ, result


class Parser:

    def __init__(self, file_path: str, only_basic_fields=False):
        if len(file_path) == 0:
            raise AttributeError('List of file paths must not be empty.')

        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                if len([file for file in zip_file.namelist() if file.endswith(".xml") or file.endswith(".gml")]) > 1:
                    print('WARNING!!! Found more than one xml/gml file in zip. Going to use only the first one.')
                for file in zip_file.namelist()[:1]:
                    if file.endswith(".xml") or file.endswith(".gml"):
                        self.file_obj: TextIO = zip_file.open(file, 'r')
                    else:
                        raise FileNotFoundError('did not find file with extensions xml or gml in provided zip')
        else:
            self.file_obj: BinaryIO = open(file_path, 'rb')

        self.NS: Namespaces = Namespaces()
        self.NS.update_from_file(self.file_obj)
        self.file_obj.seek(0)  # go back to beginning of file after reading first lines for updating namespaces
        self.Tags: Tags = Tags(self.NS)
        self.Fields: Fields = Fields(self.Tags, only_basic_fields)
        self.XML: XML = XML(self.NS, self.Tags, self.Fields)

        self.file_path: str = file_path
        self.size_mb: float = round(getsize(self.file_path) / 1024 / 1024, 4)

    def iterator(self) -> Tuple[str, List[str]]:
        """Method iterates over elements yielding values for every element."""

        tags_to_read = self.Tags.list()

        # create context for xml parser iterator
        context = etree.iterparse(
            source=self.file_obj,
            events=('end',),
            tag=tags_to_read,
            remove_blank_text=True
        )

        # parse file
        try:
            # iterate over elements
            for el in self.XML.me_xml_iterator(context):
                # parse element
                typ, result = self.XML.parse_element(el)
                vals = [result.get(k) for k in self.Fields.tag[typ]]
                # yield results as tuple with first element being tag of record and second being a list of values
                yield self.Tags.no_ns[typ], vals

        except Exception:
            print('-' * 10)
            print(datetime.now().isoformat(), '- something went wrong while parsing:')
            print(self.file_path)
            print(context.error_log)
            raise


class SQL:
    """Base class for writer classes that put data into sql databases.
    Currently syntax is compatible with PostgreSQL and SQLite. (For sqlite schema should be empty)"""
    def __init__(self, tags: Tags, fields: Fields, schema: Union[str, None]):
        self.table_name_mappings: Dict[str, str] = {
            tags.JA: 'jednostki_administracyjne',
            tags.MSC: 'miejscowosci',
            tags.UL: 'ulice',
            tags.PA: 'punkty_adresowe'
        }

        self.sql_drop: str = ''
        self.sql_create: str = ''
        self.tab_classifier: str = ''
        if schema is not None and schema not in ('', 'public'):
            self.sql_drop = 'DROP SCHEMA IF EXISTS {0} CASCADE;\n'.format(schema)
            self.sql_create = 'CREATE SCHEMA {0};\n'.format(schema)
            self.tab_classifier = schema + '.'

        for tag in tags.list():
            self.sql_drop += 'DROP TABLE IF EXISTS prg.' + self.table_name_mappings.get(tag) + ';\n'
            self.sql_create += 'CREATE TABLE prg.' + self.table_name_mappings.get(tag) + '('
            for column in fields.tag[tag]:
                self.sql_create += column + ' text, '  # all columns are text
            # remove comma and a space at the end and add closing parenthesis
            self.sql_create = self.sql_create[:-2] + ');\n'

        self.sql_insert_ja: str = 'INSERT INTO {0}{1} VALUES ({2})'.format(self.tab_classifier,
                                                                           self.table_name_mappings.get(tags.JA),
                                                                           ('%s, ' * len(fields.JA))[:-2])
        self.sql_insert_msc: str = 'INSERT INTO {0}{1} VALUES ({2})'.format(self.tab_classifier,
                                                                            self.table_name_mappings.get(tags.MSC),
                                                                            ('%s, ' * len(fields.MSC))[:-2])
        self.sql_insert_ul: str = 'INSERT INTO {0}{1} VALUES ({2})'.format(self.tab_classifier,
                                                                           self.table_name_mappings.get(tags.UL),
                                                                           ('%s, ' * len(fields.UL))[:-2])
        self.sql_insert_pa: str = 'INSERT INTO {0}{1} VALUES ({2})'.format(self.tab_classifier,
                                                                           self.table_name_mappings.get(tags.PA),
                                                                           ('%s, ' * len(fields.PA))[:-2])
        self.sql_insert: Dict[str, str] = {
            tags.no_ns[tags.PA]: self.sql_insert_pa,
            tags.no_ns[tags.JA]: self.sql_insert_ja,
            tags.no_ns[tags.MSC]: self.sql_insert_msc,
            tags.no_ns[tags.UL]: self.sql_insert_ul
        }

    def create_tables(self, conn) -> None:
        cursor = conn.cursor()
        cursor.execute(self.sql_drop)
        cursor.execute(self.sql_create)
        conn.commit()

    def inserter(self, cursor, typ: str, vals: List[str]) -> None:
        cursor.execute(self.sql_insert.get(typ), vals)


class PostgreSQLWriter(SQL):

    def __init__(self, prg_file_path: str, dsn: str, schema: Union[str, None] = 'prg', only_basic_fields: bool = False):
        self.Parser: Parser = Parser(prg_file_path, only_basic_fields)
        self.dsn: str = dsn
        super().__init__(self.Parser.Tags, self.Parser.Fields, schema)

    def run(self, prepare_tables: bool = False, commit_every: int = 50000) -> None:
        import psycopg2
        with psycopg2.connect(self.dsn) as conn:
            cursor = conn.cursor()
            if prepare_tables:
                cursor.execute(self.sql_drop)
                cursor.execute(self.sql_create)
                conn.commit()

            i = 0  # counter for inserts
            for typ, vals in self.Parser.iterator():
                cursor.execute(self.sql_insert.get(typ), vals)
                if i % commit_every == 0:
                    print(i, 'commit')
                    conn.commit()
                i += 1
            conn.commit()
            print(i, 'commit.')


class SQLiteWriter(SQL):

    def __init__(self, prg_file_path: str, db_file_path: str, only_basic_fields: bool = False):
        self.Parser: Parser = Parser(prg_file_path, only_basic_fields)
        self.db_file_path: str = db_file_path
        super().__init__(self.Parser.Tags, self.Parser.Fields, None)

    def run(self, prepare_tables: bool = False, commit_every: int = 50000):
        import sqlite3
        with sqlite3.connect(self.db_file_path) as db:
            cursor = db.cursor()
            if prepare_tables:
                db.executescript(self.sql_drop)
                db.executescript('PRAGMA journal_mode=WAL;')  # enable WAL, supposedly faster
                db.executescript(self.sql_create)
                db.commit()

            i = 0  # counter for inserts
            for typ, vals in self.Parser.iterator():
                cursor.execute(self.sql_insert.get(typ), vals)
                if i % commit_every == 0:
                    print(i, 'commit')
                    db.commit()
                i += 1
            db.commit()
            print(i, 'commit.')


class CSVWriter:

    def __init__(self, prg_file_path: str, output_directory: str, only_basic_fields: bool = False):
        self.Parser: Parser = Parser(prg_file_path, only_basic_fields)
        self.output_dir: str = output_directory
        self.output_file_paths: dict = {
            self.Parser.Tags.no_ns[x]: join(output_directory, self.Parser.Tags.no_ns[x]+'.csv')
            for x in self.Parser.Tags.list()
        }

    def run(self, headers: bool = True):
        import csv
        writers: dict = {}
        fcon: dict = {}
        for typ, fp in self.output_file_paths.items():
            if headers:
                with open(fp, 'w', encoding='UTF-8', newline='') as f:
                    csv.DictWriter(f, self.Parser.Fields.tag.get(self.Parser.Tags.with_ns[typ])).writeheader()

            fcon[typ] = open(fp, 'a', encoding='UTF-8', newline='')
            writers[typ] = csv.writer(fcon[typ])

        for typ, vals in self.Parser.iterator():
            writers[typ].writerow(vals)

        for f in fcon.values():
            f.close()


class StdOutWriter:

    def __init__(self, prg_file_path: str, only_basic_fields: bool = False):
        self.Parser: Parser = Parser(prg_file_path, only_basic_fields)

    def run(self, limit: Union[int, None] = None):
        import csv
        import os
        from sys import stdout
        from io import StringIO
        strio = StringIO()
        writer = csv.writer(strio, lineterminator=os.linesep)
        i = 1  # counter for limit
        for typ, vals in self.Parser.iterator():
            if limit and i > limit:
                break
            writer.writerow(vals)
            stdout.write(self.Parser.Tags.no_ns2short[typ]+'|'+strio.getvalue())
            i += 1


if __name__ == '__main__':
    def str2bool(v) -> bool:
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='File path to the input file.', nargs=1)
    parser.add_argument('--writer', help='Writer to use.', choices=('csv', 'sqlite', 'postgresql', 'stdout'), nargs=1)
    parser.add_argument('--csv_directory', help='Directory for csv files when using csv writer.', nargs=1)
    parser.add_argument('--sqlite_file', help='Filepath for SQLite database when using sqlite writer.', nargs=1)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL when using postgresql writer.', nargs=1)
    parser.add_argument('--prep_tables', help='Drop and create tables when using db writers.',
                        nargs='?',
                        type=str2bool,
                        const=True)
    parser.add_argument('--limit', help='Limit number of parsed rows when using stdout writer. Mostly for testing.',
                        nargs=1,
                        type=int)
    args = vars(parser.parse_args())

    sqlparams = {}
    if args['prep_tables']:
        sqlparams['prepare_table'] = args['prep_tables']

    if args['writer'][0] == 'stdout':
        StdOutWriter(args['input'][0]).run(limit=args['limit'][0] if args['limit'] else None)
    elif args['writer'][0] == 'csv':
        CSVWriter(args['input'][0], args['csv_directory'][0]).run()
    elif args['writer'][0] == 'sqlite':
        SQLiteWriter(args['input'][0], args['sqlite_file'][0]).run(**sqlparams)
    elif args['writer'][0] == 'postgresql':
        PostgreSQLWriter(args['input'][0], args['dsn'][0]).run(**sqlparams)
    else:
        print(args)
