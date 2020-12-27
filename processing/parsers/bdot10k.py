"""Modified version of prg.py script. Currently quite hacky..."""
import os
import zipfile
from os.path import getsize, join
import re
from datetime import datetime
from typing import List, Union, Dict, Set, Tuple, TextIO, BinaryIO
from collections import OrderedDict
import argparse

from lxml import etree


lookup_x_kod = {
    'BUBD01': 'budynki mieszkalne jednorodzinne',
    'BUBD02': 'budynki o dwóch mieszkaniach',
    'BUBD03': 'budynki o trzech i więcej mieszkaniach',
    'BUBD04': 'budynki zbiorowego zamieszkania',
    'BUBD05': 'budynki hoteli',
    'BUBD06': 'budynki zakwaterowania turystycznego, pozostałe',
    'BUBD07': 'budynki biurowe',
    'BUBD08': 'budynki handlowo-usługowe',
    'BUBD09': 'budynki łączności, dworców i terminali',
    'BUBD10': 'budynki garaży',
    'BUBD11': 'budynki przemysłowe',
    'BUBD12': 'zbiorniki, silosy i budynki magazynowe',
    'BUBD13': 'ogólnodostępne obiekty kulturalne',
    'BUBD14': 'budynki muzeów i bibliotek',
    'BUBD15': 'budynki szkół i instytucji badawczych',
    'BUBD16': 'budynki szpitali i zakładów opieki medycznej',
    'BUBD17': 'budynki kultury fizycznej',
    'BUBD18': 'budynki gospodarstw rolnych',
    'BUBD19': 'budynki przeznaczone do sprawowania kultu religijnego i czynności religijnych',
    'BUBD20': 'obiekty budowlane wpisane do rejestru zabytków i objęte indywidualną ochroną konserwatorską oraz nieruchome, archeologiczne dobra kultury',
    'BUBD21': 'pozostałe budynki niemieszkalne, gdzie indziej nie wymienione',
}

lookup_x_katIstnienia = {
    'Eks': 'eksploatowany',
    'Bud': 'w budowie',
    'Zns': 'zniszczony',
    'Tmc': 'tymczasowy',
    'Ncn': 'nieczynny',
}

lookup_funOgolnaBudynku = {
    '1110': 'budynki mieszkalne jednorodzinne',
    '1121': 'budynki o dwóch mieszkaniach',
    '1122': 'budynki o trzech i więcej mieszkaniach',
    '1130': 'budynki zbiorowego zamieszkani',
    '1211': 'budynki hoteli',
    '1212': 'pozostałe budynki zakwaterowania turystycznego',
    '1220': 'budynki biurowe',
    '1230': 'budynki handlowo-usługowe',
    '1241': 'budynki łączności dworców i terminali',
    '1242': 'garaże',
    '1251': 'budynki przemysłowe',
    '1252': 'zbiorniki, silosy lub budynki magazynowe',
    '1261': 'ogólnodostępne budynki kulturalne',
    '1262': 'muzea lub biblioteki',
    '1263': 'budynki szkół i instytucji badawczych',
    '1264': 'budynki szpitali i zakładów opieki medyczne',
    '1265': 'budynki kultury fizycznej',
    '1271': 'budynki gospodarstwa rolnego',
    '1272': ' budynki kultu religijnego',
    '1273': 'budynek zabytkowy',
    '1274': 'pozostałe budynki niemieszkalne',
}

lookup_funSzczegolowaBudynku = {
    '1110.Dj': 'budynek jednorodzinny',
    '1110.Dl': 'dom letniskowy',
    '1110.Ls': 'leśniczówka',
    '1121.Db': 'budynek o dwóch mieszkaniach',
    '1122.Dw': 'budynek wielorodzinny',
    '1130.Bs': 'bursa szkolna',
    '1130.Db': 'dom dla bezdomnych',
    '1130.Dd': 'dom dziecka',
    '1130.Os': 'dom opieki społecznej',
    '1130.Dp': 'dom parafialny',
    '1130.Ds': 'dom studencki',
    '1130.Dz': 'dom zakonny',
    '1130.Hr': 'hotel robotniczy',
    '1130.In': 'internat',
    '1130.Kl': 'klasztor',
    '1130.Km': 'koszary',
    '1130.Po': 'placówka opiekuńczo-wychowawcza',
    '1130.Ra': 'rezydencja ambasadora',
    '1130.Rb': 'rezydencja biskupia',
    '1130.Rp': 'rezydencja prezydencka',
    '1130.Zk': 'zakład karny',
    '1130.Zp': 'zakład poprawczy',
    '1211.Dw': 'dom weselny',
    '1211.Ht': 'hotel',
    '1211.Mt': 'motel',
    '1211.Pj': 'pensjonat',
    '1211.Rj': 'restauracja',
    '1211.Zj': 'zajazd',
    '1212.Dk': 'domek kempingowy',
    '1212.Dr': 'dom rekolekcyjny',
    '1212.Dw': 'dom wypoczynkowy',
    '1212.Os': 'ośrodek szkoleniowo wypoczynkowy',
    '1212.St': 'schronisko turystyczne',
    '1220.Bk': 'bank',
    '1220.Ck': 'centrum konferencyjne',
    '1220.Km': 'Kuria Metropolitarna',
    '1220.Mn': 'ministerstwo',
    '1220.Pd': 'placówka dyplomatyczna lub konsularna',
    '1220.Pc': 'policja',
    '1220.Pk': 'prokuratura',
    '1220.Pg': 'przejście graniczne',
    '1220.Sd': 'sąd',
    '1220.Sf': 'siedziba firmy lub firm',
    '1220.Pw': 'Starostwo Powiatowe',
    '1220.Sg': 'straż graniczna',
    '1220.Sp': 'straż pożarna',
    '1220.Uc': 'Urząd Celny',
    '1220.Ug': 'Urząd Gminy',
    '1220.Um': 'Urząd Miasta',
    '1220.Umg': 'Urząd Miasta i Gminy',
    '1220.Mr': 'Urząd Marszałkowski',
    '1220.Up': 'placówka operatora pocztowego',
    '1220.Uw': 'Urząd Wojewódzki',
    '1220.Ap': 'inny urząd administracji publicznej',
    '1230.Ap': 'apteka',
    '1230.Ch': 'centrum handlowe',
    '1230.Dh': 'dom towarowy lub handlowy',
    '1230.Ht': 'hala targowa',
    '1230.Hw': 'hala wystawowa',
    '1230.Hm': 'hipermarket lub supermarket',
    '1230.Ph': 'pawilon handlowo-usługowy',
    '1230.So': 'stacja obsługi pojazdów',
    '1230.Sp': 'stacja paliw',
    '1241.Kk': 'budynek kontroli ruchu kolejowego',
    '1241.Kp': 'budynek kontroli ruchu powietrznego',
    '1241.Ct': 'centrum telekomunikacyjne',
    '1241.Da': 'dworzec autobusowy',
    '1241.Dk': 'dworzec kolejowy',
    '1241.Dl': 'dworzec lotniczy',
    '1241.Hg': 'hangar',
    '1241.Lm': 'latarnia morska',
    '1241.Lk': 'lokomotywownia lub wagonownia',
    '1241.Kg': 'stacja kolejki górskiej lub wyciągu krzesełkowego',
    '1241.Rt': 'stacja nadawcza radia i telewizji',
    '1241.Tp': 'terminal portowy',
    '1241.Ab': 'zajezdnia autobusowa',
    '1241.Tr': 'zajezdnia tramwajowa',
    '1241.Tb': 'zajezdnia trolejbusowa',
    '1242.Gr': 'garaż',
    '1242.Pw': 'parking wielopoziomowy',
    '1251.El': 'elektrociepłownia',
    '1251.Ek': 'elektrownia',
    '1251.Kt': 'kotłownia',
    '1251.Mn': 'młyn',
    '1251.Pr': 'produkcyjny',
    '1251.Rf': 'rafineria',
    '1251.Ss': 'spalarnia śmieci',
    '1251.Wr': 'warsztat remontowo-naprawczy',
    '1251.Wt': 'wiatrak',
    '1252.Sp': 'budynek spedycji',
    '1252.Ch': 'chłodnia',
    '1252.El': 'elewator',
    '1252.Mg': 'magazyn',
    '1252.Sl': 'silos',
    '1252.Gz': 'zbiornik na gaz',
    '1252.Ci': 'zbiornik na ciecz',
    '1261.Oz': 'budynek ogrodu zoo lub botanicznego',
    '1261.Dk': 'dom kultury',
    '1261.Fh': 'filharmonia',
    '1261.Hw': 'hala widowiskowa',
    '1261.Ks': 'kasyno',
    '1261.Kn': 'kino',
    '1261.Kl': 'klub, dyskoteka',
    '1261.Op': 'opera',
    '1261.Sz': 'schronisko dla zwierząt',
    '1261.Tt': 'teatr',
    '1262.Ar': 'archiwum',
    '1262.Bl': 'biblioteka',
    '1262.Ci': 'centrum informacyjne',
    '1262.Gs': 'galeria sztuki',
    '1262.Mz': 'muzeum',
    '1263.Ob': 'obserwatorium lub planetarium',
    '1263.Pb': 'placówka badawcza',
    '1263.Ps': 'przedszkole',
    '1263.Sh': 'stacja hydrologiczna',
    '1263.Sm': 'stacja meteorologiczna',
    '1263.Sp': 'szkoła podstawowa',
    '1263.Sd': 'szkoła ponadpodstawowa',
    '1263.Sw': 'szkoła wyższa',
    '1264.Hs': 'hospicjum',
    '1264.Iw': 'izba wytrzeźwień',
    '1264.Jr': 'jednostka ratownictwa medycznego',
    '1264.Kw': 'klinika weterynaryjna',
    '1264.Oo': 'ośrodek opieki społecznej',
    '1264.Po': 'placówka ochrony zdrowia',
    '1264.St': 'sanatorium',
    '1264.Sk': 'stacja krwiodawstwa',
    '1264.Ss': 'stacja sanitarno-epidemiologiczna',
    '1264.Sz': 'szpital',
    '1264.Zb': 'żłobek',
    '1265.Hs': 'hala sportowa',
    '1265.Ht': 'halowy tor gokartowy',
    '1265.Ks': 'klub sportowy',
    '1265.Kt': 'korty tenisowe',
    '1265.Kr': 'kręgielnia',
    '1265.Pl': 'pływalnia',
    '1265.Sg': 'sala gimnastyczna',
    '1265.St': 'strzelnica',
    '1265.Sl': 'sztuczne lodowisko',
    '1265.Uj': 'ujeżdżalnia',
    '1271.Bg': 'budynek gospodarczy',
    '1271.Bp': 'budynek produkcyjny zwierząt hodowlanych',
    '1271.St': 'stajnia',
    '1271.Sz': 'szklarnia lub cieplarnia',
    '1272.Bc': 'budynki cmentarne',
    '1272.Ck': 'cerkiew',
    '1272.Dp': 'dom pogrzebowy',
    '1272.Dz': 'dzwonnica',
    '1272.Ir': 'inny budynek kultu religijnego',
    '1272.Kp': 'kaplica',
    '1272.Ks': 'kościół',
    '1272.Kr': 'krematorium',
    '1272.Mc': 'meczet',
    '1272.Sn': 'synagoga',
    '1273.Zb': 'zabytek bez funkcji użytkowej',
    '1274.As': 'areszt śledczy',
    '1274.Bc': 'bacówka',
    '1274.Sc': 'schronisko dla nieletnich',
    '1274.Sg': 'stacja gazowa',
    '1274.Sp': 'stacja pomp',
    '1274.St': 'stacja transformatorowa',
    '1274.Tp': 'toaleta publiczna',
    '1274.Zk': 'zabudowania koszarowe',
    '1274.Zp': 'zakład karny lub poprawczy',
}


class Namespaces:

    def __init__(self):
        # initial namespaces
        # XLINK is an exception being namespace with a tag already since it's pretty much the only use of it anyway
        self.XLINK: str = r'{http://www.w3.org/1999/xlink}href'
        self.NS_MZ: str = r'urn:gugik:specyfikacje:gmlas:mapaZasadnicza:1.0'
        self.NS_OT: str = r'urn:gugik:specyfikacje:gmlas:bazaDanychObiektowTopograficznych10k:1.0'
        self.NS_GML: str = r'http://www.opengis.net/gml/3.2'
        self.NS_XSI: str = r'http://www.w3.org/2001/XMLSchema-instance'
        self.NS_BT: str = r'urn:gugik:specyfikacje:gmlas:modelPodstawowy:1.0'
        self.NS_GMD: str = r'http://www.isotc211.org/2005/gmd'
        self.NS_GCO: str = r'http://www.isotc211.org/2005/gco'

    def update_from_file(self, file_obj: Union[TextIO, BinaryIO]) -> None:
        """Updates namespaces in the class from xml file by looking at the file's first 15 lines."""
        for _ in range(15):
            line = file_obj.readline() if type(file_obj.readline()) == str else file_obj.readline().decode('UTF-8')
            re_ns_mz = re.search(
                r'(urn:gugik:specyfikacje:gmlas:mapaZasadnicza:\d\.\d)',
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
            re_ns_ot = re.search(
                r'(urn:gugik:specyfikacje:gmlas:bazaDanychObiektowTopograficznych10k:\d\.\d)',
                line,
                flags=re.RegexFlag.IGNORECASE
            )
            if re_ns_mz:
                self.NS_MZ = re_ns_mz.group(1)
            if re_ns_gml:
                self.NS_GML = re_ns_gml.group(1)
            if re_ns_bt:
                self.NS_BT = re_ns_bt.group(1)
            if re_ns_ot:
                self.NS_OT = re_ns_ot.group(1)


class Tags:
    def __init__(self, namespaces: Namespaces):
        self.BUBD: str = '{' + namespaces.NS_OT + '}OT_BUBD_A'
        # self.BUIN: str = '{' + namespaces.NS_OT + '}OT_BUIN_L'
        # self.BUHD: str = '{' + namespaces.NS_OT + '}OT_BUHD_L'
        # self.BUHD: str = '{' + namespaces.NS_OT + '}OT_BUHD_P'
        # self.BUSP: str = '{' + namespaces.NS_OT + '}OT_BUSP_A'
        # self.BUSP: str = '{' + namespaces.NS_OT + '}OT_BUSP_L'
        # self.BUWT: str = '{' + namespaces.NS_OT + '}OT_BUWT_A'
        # self.BUWT: str = '{' + namespaces.NS_OT + '}OT_BUWT_P'
        # self.BUBD: str = '{' + namespaces.NS_OT + '}OT_BUBD_A'

        self.no_ns: dict = {
            self.BUBD: 'OT_BUBD_A',
        }
        self.with_ns: dict = {
            'OT_BUBD_A': self.BUBD,
        }
        self.no_ns2short: dict = {
            'OT_BUBD_A': 'BUBD_A',
        }

    def list(self) -> Set[str]:
        result = set()
        result.add(self.BUBD)
        return result


class Fields:

    def __init__(self, tags: Tags, only_basic_fields: bool = False):
        self.Tags: Tags = tags
        self.BUBD: OrderedDict[str, None] = OrderedDict()
        self.set_default_fields()
        if only_basic_fields:
            self.set_only_basic_fields()
        else:
            self.set_default_fields()
        self.tag: Dict[str, OrderedDict[str, None]] = {
            self.Tags.BUBD: self.BUBD,
        }

    def set_default_fields(self):
        self.BUBD = OrderedDict.fromkeys([
            'gmlid',
            'lokalnyId',
            'przestrzenNazw',
            'wersjaId',
            'czyObiektBDOO',
            'x_kod',
            'x_skrKarto',
            'x_katDoklGeom',
            'x_doklGeom',
            'x_zrodloDanychG',
            'x_zrodloDanychA',
            'x_katIstnienia',
            'x_rodzajReprGeom',
            'x_uzytkownik',
            'x_aktualnoscG',
            'x_aktualnoscA',
            'poczatekWersjiObiektu',
            'koniecWersjiObiektu',
            'x_uwagi',
            'x_dataUtworzenia',
            'x_informDodatkowa',
            'x_kodKarto10k',
            'x_kodKarto25k',
            'x_kodKarto50k',
            'x_kodKarto100k',
            'x_kodKarto250k',
            'x_kodKarto500k',
            'x_kodKarto1000k',
            'funOgolnaBudynku',
            'funSzczegolowaBudynku',
            'liczbaKondygnacji',
            'kodKst',
            'nazwa',
            'zabytek',
            'geometry',
        ])

    def set_only_basic_fields(self):
        self.set_default_fields()
        fields_to_remove = [
            'gmlid',
            'przestrzenNazw',
            'czyObiektBDOO',
            'x_katDoklGeom',
            'x_doklGeom',
            'x_zrodloDanychG',
            'x_zrodloDanychA',
            'x_rodzajReprGeom',
            'x_uzytkownik',
            'poczatekWersjiObiektu',
            'x_uwagi',
            'x_dataUtworzenia',
            'x_informDodatkowa',
            'x_kodKarto10k',
            'x_kodKarto25k',
            'x_kodKarto50k',
            'x_kodKarto100k',
            'x_kodKarto250k',
            'x_kodKarto500k',
            'x_kodKarto1000k',
        ]
        for key in fields_to_remove:
            del self.BUBD[key]

    def remove_fields(self, fields: List[str]) -> None:
        for key in fields:
            if key in self.BUBD:
                del self.BUBD[key]


class XML:

    def __init__(self, namespaces: Namespaces, tags: Tags, fields: Fields):
        self.NS: Namespaces = namespaces
        self.geometry_names: Set[str] = {'geometria'}
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
            name = x.tag

            # if no children and fields in the list of fields we want the values of
            # add data to dictionary
            if len(list(x)) == 0 and name in self.Fields.tag[typ]:
                # lokalnyid tag exists twice within a record, we will keep only the first
                if name in result:
                    continue
                # old stuff from prg parser
                # # some tags appear multiple times with different values
                # # but not attribute to make them distinct
                # # so if we already have a key present
                # # create new key with appended 2 digit number
                # # if tag has empty text but contains xlink xref attribute
                # # then take that as a value
                # if name in result:
                #     last_name = sorted([x for x in result.keys() if str(x).startswith(name)], reverse=True)[0]
                #     name = incremented_name(last_name)
                # # if value or href link start with url 'http://geoportal.gov.pl/PZGIK/dane/',
                # # remove it as it is not necessary
                # if x.text and x.text.startswith('http://geoportal.gov.pl'):
                #     val = str(x.text)[35:]
                # elif x.text is None and x.get(self.NS.XLINK) and x.get(self.NS.XLINK).startswith('http://geoportal.gov.pl'):
                #     val = str(x.get(self.NS.XLINK))[35:]
                # else:
                #     val = x.text
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
                for file in [f for f in zip_file.namelist() if f.endswith('OT_BUBD_A.xml')]:
                    self.file_obj: TextIO = zip_file.open(file, 'r')
        else:
            self.file_obj: BinaryIO = open(file_path, 'rb')

        self.powiat = re.search(r'BDOT10k_(\d{4})\.zip',
                                os.path.basename(file_path),
                                flags=re.RegexFlag.IGNORECASE
                                ).group(1)

        self.NS: Namespaces = Namespaces()
        self.NS.update_from_file(self.file_obj)
        self.file_obj.seek(0)  # go back to beginning of file after reading first lines for updating namespaces
        self.Tags: Tags = Tags(self.NS)
        self.Fields: Fields = Fields(self.Tags, only_basic_fields)

        # adding powiat field manually
        if self.powiat:
            self.Fields.BUBD['powiat'] = None

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

                # adding powiat value manually
                result['powiat'] = self.powiat

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

    def __init__(self, tags: Tags, fields: Fields, schema: Union[str, None], prep_st_placeholder: str):
        self.table_name_mappings: Dict[str, str] = {
            tags.BUBD: 'stg_budynki_ogolne_poligony',
        }

        self.sql_drop: str = ''
        self.sql_create: str = ''
        self.tab_classifier: str = ''
        if schema is not None and schema not in ('', 'public'):
            self.sql_create = 'CREATE SCHEMA IF NOT EXISTS {0};\n'.format(schema)
            self.tab_classifier = schema + '.'

        for tag in tags.list():
            self.sql_drop += 'DROP TABLE IF EXISTS ' + self.tab_classifier + self.table_name_mappings.get(tag) + ' CASCADE;\n'
            self.sql_create += 'CREATE TABLE ' + self.tab_classifier + self.table_name_mappings.get(tag) + '('
            for column in fields.tag[tag]:
                self.sql_create += column + ' text, '  # all columns are text
            # remove comma and a space at the end and add closing parenthesis
            self.sql_create = self.sql_create[:-2] + ');\n'

        self.sql_insert_bubd: str = 'INSERT INTO {0}{1} VALUES ({2})'.format(self.tab_classifier,
                                                                             self.table_name_mappings.get(tags.BUBD),
                                                                             ((prep_st_placeholder + ', ') * len(fields.BUBD))[:-2])

        self.sql_insert: Dict[str, str] = {
            tags.no_ns[tags.BUBD]: self.sql_insert_bubd,
        }

    def create_tables(self, conn) -> None:
        cursor = conn.cursor()
        cursor.execute(self.sql_drop)
        cursor.execute(self.sql_create)
        conn.commit()

    def inserter(self, cursor, typ: str, vals: List[str]) -> None:
        cursor.execute(self.sql_insert.get(typ), vals)


class PostgreSQLWriter(SQL):

    def __init__(self, prg_file_path: str, dsn: str, schema: Union[str, None] = 'bdot', only_basic_fields: bool = False):
        self.Parser: Parser = Parser(prg_file_path, only_basic_fields)
        self.dsn: str = dsn
        self.schema: str = schema
        super().__init__(self.Parser.Tags, self.Parser.Fields, schema, '%s')

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

    def create_lookup_tables(self):
        import psycopg2
        with psycopg2.connect(self.dsn) as conn:
            cursor = conn.cursor()
            t_lookup_x_kod = f"{self.schema + '.' if self.schema else ''}lookup_x_kod"
            t_lookup_x_katIstnienia = f"{self.schema + '.' if self.schema else ''}lookup_x_katIstnienia"
            t_lookup_funOgolnaBudynku = f"{self.schema + '.' if self.schema else ''}lookup_funOgolnaBudynku"
            t_lookup_funSzczegolowaBudynku = f"{self.schema + '.' if self.schema else ''}lookup_funSzczegolowaBudynku"
            query = f"""
                CREATE TABLE IF NOT EXISTS {t_lookup_x_kod} (
                    x_kod text primary key, 
                    kategoria_bdot text not null
                );
                CREATE TABLE IF NOT EXISTS {t_lookup_x_katIstnienia} (
                    x_katIstnienia text primary key,
                    status_bdot text not null
                );
                CREATE TABLE IF NOT EXISTS {t_lookup_funOgolnaBudynku} (
                    funOgolnaBudynku text primary key,
                    funkcja_ogolna_budynku text not null
                );
                CREATE TABLE IF NOT EXISTS {t_lookup_funSzczegolowaBudynku} (
                    funSzczegolowaBudynku text primary key,
                    funkcja_szczegolowa_budynku text not null
                );
            """
            cursor.execute(query)
            for k, v in lookup_x_kod.items():
                cursor.execute(f'INSERT INTO {t_lookup_x_kod} VALUES (%s, %s) ON CONFLICT DO NOTHING', (k, v))
            for k, v in lookup_x_katIstnienia.items():
                cursor.execute(f'INSERT INTO {t_lookup_x_katIstnienia} VALUES (%s, %s) ON CONFLICT DO NOTHING', (k, v))
            for k, v in lookup_funOgolnaBudynku.items():
                cursor.execute(f'INSERT INTO {t_lookup_funOgolnaBudynku} VALUES (%s, %s) ON CONFLICT DO NOTHING', (k, v))
            for k, v in lookup_funSzczegolowaBudynku.items():
                cursor.execute(f'INSERT INTO {t_lookup_funSzczegolowaBudynku} VALUES (%s, %s) ON CONFLICT DO NOTHING', (k, v))
            conn.commit()

    def create_view(self):
        import psycopg2
        with psycopg2.connect(self.dsn) as conn:
            cursor = conn.cursor()
            t_lookup_x_kod = f"{self.schema + '.' if self.schema else ''}lookup_x_kod"
            t_lookup_x_katIstnienia = f"{self.schema + '.' if self.schema else ''}lookup_x_katIstnienia"
            t_lookup_funOgolnaBudynku = f"{self.schema + '.' if self.schema else ''}lookup_funOgolnaBudynku"
            t_lookup_funSzczegolowaBudynku = f"{self.schema + '.' if self.schema else ''}lookup_funSzczegolowaBudynku"
            v_name = f"{self.schema + '.' if self.schema else ''}v_bubd_a"
            t_bubd_a = f"{self.schema + '.' if self.schema else ''}" + self.table_name_mappings.get(self.Parser.Tags.BUBD)
            query = f"""
                CREATE OR REPLACE VIEW {v_name} as
                    SELECT 
                        powiat,
                        lokalnyid,
                        cast(wersjaid as timestamp) wersjaid,
                        status_bdot,
                        nazwa,
                        kategoria_bdot,
                        funkcja_ogolna_budynku,
                        funkcja_szczegolowa_budynku,
                        cast(liczbakondygnacji as smallint) liczba_kondygnacji,
                        zabytek,
                        x_skrkarto skrot_karto,
                        cast(x_aktualnoscg as date) aktualnosc_geometrii,
                        cast(x_aktualnosca as date) aktualnosc_atrybutow,
                        cast(koniecwersjiobiektu as timestamp) koniecwersjiobiektu,
                        kodkst kod_kst,
                        ST_GeomFromGML(SUBSTRING(geometry, 54, length(geometry) - 64)) geom_a_2180
                    FROM {t_bubd_a}
                    LEFT JOIN {t_lookup_x_kod} using (x_kod)
                    LEFT JOIN {t_lookup_x_katIstnienia} using (x_katIstnienia)
                    LEFT JOIN {t_lookup_funOgolnaBudynku} using (funOgolnaBudynku)
                    LEFT JOIN {t_lookup_funSzczegolowaBudynku} using (funSzczegolowaBudynku)
            """
            cursor.execute(query)
            conn.commit()


class SQLiteWriter(SQL):

    def __init__(self, prg_file_path: str, db_file_path: str, only_basic_fields: bool = False):
        self.Parser: Parser = Parser(prg_file_path, only_basic_fields)
        self.db_file_path: str = db_file_path
        super().__init__(self.Parser.Tags, self.Parser.Fields, None, '?')

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
        prg_fn = os.path.basename(prg_file_path).split('.')[0]
        self.output_file_paths: dict = {
            self.Parser.Tags.no_ns[x]: join(output_directory, prg_fn + self.Parser.Tags.no_ns[x] + '.csv')
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
            stdout.write(self.Parser.Tags.no_ns2short[typ] + '|' + strio.getvalue())
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
    parser.add_argument('--input', help='File paths to the input files. (provide one or more)', nargs='+')
    parser.add_argument('--writer', help='Writer to use.', choices=('csv', 'sqlite', 'postgresql', 'stdout'), nargs=1)
    parser.add_argument('--csv_directory', help='Directory for csv files when using csv writer.', nargs=1)
    parser.add_argument('--sqlite_file', help='Filepath for SQLite database when using sqlite writer.', nargs=1)
    parser.add_argument('--dsn', help='Connection string for PostgreSQL when using postgresql writer.', nargs=1)
    parser.add_argument('--prep_tables', help='Drop and create tables when using db writers.',
                        nargs='?',
                        type=str2bool,
                        const=True)
    parser.add_argument('--basic_fields', help='Only leave basic fields.',
                        nargs='?',
                        type=str2bool,
                        const=True)
    parser.add_argument('--create_view', help='Only for PostgreSQL. Create view using lookup tables.',
                        nargs='?',
                        type=str2bool,
                        const=True)
    parser.add_argument('--create_lookup_tables', help='Only for PostgreSQL. Create lookup tables.',
                        nargs='?',
                        type=str2bool,
                        const=True)
    parser.add_argument('--limit', help='Limit number of parsed rows when using stdout writer. Mostly for testing.',
                        nargs=1,
                        type=int)
    parser.add_argument('--csv_headers', help='Add headers while writing csv files (enabled by default).',
                        nargs='?',
                        type=str2bool,
                        const=True)
    args = vars(parser.parse_args())

    params = {}

    file_paths = args['input']

    for idx, file_path in enumerate(file_paths):
        print(str(idx+1).zfill(3), '-', file_path)

        if idx == 0 and args['prep_tables']:
            params['prepare_tables'] = args['prep_tables']
        else:
            params = {}

        if args['writer'][0] == 'stdout':
            StdOutWriter(file_path, only_basic_fields=args['basic_fields']).run(limit=args['limit'][0] if args['limit'] else None)
        elif args['writer'][0] == 'csv':
            CSVWriter(file_path, args['csv_directory'][0], only_basic_fields=args['basic_fields']).run(headers=args['csv_headers'][0] if args['csv_headers'] else True)
        elif args['writer'][0] == 'sqlite':
            SQLiteWriter(file_path, args['sqlite_file'][0], only_basic_fields=args['basic_fields']).run(**params)
        elif args['writer'][0] == 'postgresql':
            pgw = PostgreSQLWriter(file_path, args['dsn'][0], only_basic_fields=args['basic_fields'])
            pgw.run(**params)
            if idx == 0 and args['create_lookup_tables']:
                pgw.create_lookup_tables()
            if idx == 0 and args['create_view']:
                pgw.create_view()
        else:
            print(args)
