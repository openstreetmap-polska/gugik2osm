import json
from dataclasses import dataclass
from typing import Callable, List, Dict, Any, Tuple

from .database import QUERIES, data_from_db, execute_batch
from .util import addresses_nodes, buildings_nodes
from . import util


@dataclass(frozen=True)
class LayerDefinition:
    id: str
    name: str
    query_by_id: str
    query_by_bbox: str
    convert_to_xml_element: Callable
    export_parameter_name: str
    active: bool = True
    default: bool = False
    warning: str = ''

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other


# def data(self, parameters: QueryParametersType) -> QueryOutputType:
#     with pgdb().cursor() as cur:
#         cur = execute_sql(cur, parameters)
#         results = cur.fetchall()
#     return results


class Layers:

    _list_of_layers = [
        LayerDefinition(
            id='addresses_to_import',
            name='Adresy brakujące w OSM',
            query_by_id=QUERIES['delta_where_id'],
            query_by_bbox=QUERIES['delta_where_bbox'],
            convert_to_xml_element=addresses_nodes,
            export_parameter_name='lb_adresow',
            active=True,
            default=True
        ),
        LayerDefinition(
            id='buildings_to_import',
            name='Budynki brakujące w OSM',
            query_by_id=QUERIES['buildings_vertices_where_id'],
            query_by_bbox=QUERIES['buildings_vertices'],
            convert_to_xml_element=buildings_nodes,
            export_parameter_name='lb_budynkow',
            active=True,
            default=True
        ),
        LayerDefinition(
            id='addresses',
            name='Wszystkie adresy z PRG',
            query_by_id=QUERIES['addresses_all_where_id'],
            query_by_bbox=QUERIES['addresses_all_where_bbox'],
            convert_to_xml_element=addresses_nodes,
            export_parameter_name='lb_adresow',
            active=True,
            default=False,
            warning='Nie nadaje się do bezpośredniego importu. ' +
                    'Ta warstwa zawiera wszystkie adresy z PRG na danym obszarze ' +
                    'i służy do podmieniania istniejących w OSM adresów. Dla zaawansowanych edytorów.'
        ),
        LayerDefinition(
            id='buildings',
            name='Wszystkie budynki z BDOT10k',
            query_by_id=QUERIES['buildings_all_id'],
            query_by_bbox=QUERIES['buildings_all_bbox'],
            convert_to_xml_element=buildings_nodes,
            export_parameter_name='lb_budynkow',
            active=True,
            default=False,
            warning='Nie nadaje się do bezpośredniego importu. ' +
                    'Ta warstwa zawiera wszystkie budynki (z warstwy BUBD) z BDOT10k na danym obszarze ' +
                    'i służy do podmieniania geometrii istniejących w OSM budynków. Dla zaawansowanych edytorów.'
        ),
    ]
    _dict_of_layers = {layer.id: layer for layer in _list_of_layers}

    @property
    def active(self) -> List[LayerDefinition]:
        return [layer for layer in self._list_of_layers if layer.active]

    @property
    def default(self) -> List[LayerDefinition]:
        return [layer for layer in self._list_of_layers if layer.default]

    @property
    def all(self) -> List[LayerDefinition]:
        return self._list_of_layers

    @property
    def active_ids(self) -> List[str]:
        return [layer.id for layer in self.active]

    @property
    def active_ids_with_names(self) -> List[Dict[str, str]]:
        return [
            {'id': layer.id, 'name': layer.name, 'default': layer.default, 'warning': layer.warning}
            for layer in self.active
        ]

    def __getitem__(self, item) -> LayerDefinition:
        return self._dict_of_layers[item]


@dataclass
class ProposedAddress:
    id: str
    city: str
    teryt_simc: str
    street: str
    house_number: str
    post_code: str
    geometry: Dict[str, Any]

    @property
    def id_tags_geom_tuple(self) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        tags = {'addr:housenumber': self.house_number, 'source:addr': 'gugik.gov.pl'}
        if self.post_code:
            tags['addr:postcode'] = self.post_code
        if self.teryt_simc:
            tags['addr:city:simc'] = self.teryt_simc
        if self.street:
            tags['addr:street'] = self.street
            tags['addr:city'] = self.city
        else:
            tags['addr:place'] = self.city
        return self.id, tags, self.geometry


def proposed_addresses(bbox: Tuple[float, float, float, float]) -> List[ProposedAddress]:
    data = data_from_db(QUERIES['sc_proposed_addresses_in_bbox'], bbox)
    return [ProposedAddress(*a[:6], json.loads(a[6])) for a in data]


def proposed_addresses_geojson_dict(bbox: Tuple[float, float, float, float]) -> Dict[str, Any]:
    pa = proposed_addresses(bbox)
    data = [x.id_tags_geom_tuple for x in pa]
    features = [util.Feature(id=x[0], tags=x[1], geojson_geometry=x[2]) for x in data]
    return util.to_geojson_dict(features)


def report_addresses(ids: List[str]) -> None:
    execute_batch(QUERIES['insert_to_exclude_prg'], [(x,) for x in ids])


@dataclass
class ProposedBuilding:
    id: str
    building: str
    amenity: str
    man_made: str
    leisure: str
    historic: str
    tourism: str
    building_levels: int
    geometry: Dict[str, Any]

    @property
    def id_tags_geom_tuple(self) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        tags = {'source': 'www.geoportal.gov.pl'}
        if self.building:
            tags['building'] = self.building
        if self.amenity:
            tags['amenity'] = self.amenity
        if self.man_made:
            tags['man_made'] = self.man_made
        if self.leisure:
            tags['leisure'] = self.leisure
        if self.historic:
            tags['historic'] = self.historic
        if self.tourism:
            tags['tourism'] = self.tourism
        if self.building_levels:
            tags['building:levels'] = self.building_levels
        return self.id, tags, self.geometry


def proposed_buildings(bbox: Tuple[float, float, float, float]) -> List[ProposedBuilding]:
    data = data_from_db(QUERIES['sc_proposed_buildings_in_bbox'], bbox)
    return [ProposedBuilding(*a[:8], json.loads(a[8])) for a in data]


def proposed_buildings_geojson_dict(bbox: Tuple[float, float, float, float]) -> Dict[str, Any]:
    pb = proposed_buildings(bbox)
    data = [x.id_tags_geom_tuple for x in pb]
    features = [util.Feature(id=x[0], tags=x[1], geojson_geometry=x[2]) for x in data]
    return util.to_geojson_dict(features)


def report_buildings(ids: List[str]) -> None:
    execute_batch(QUERIES['insert_to_exclude_bdot_buildings'], [(x,) for x in ids])
