import json
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Union

from . import util
from . import database as db


@dataclass(frozen=True)
class LayerDefinition:
    id: str
    parent_id: str
    name: str
    query_by_id: str
    query_by_bbox: str
    export_parameter_name: str
    active: bool = True
    default: bool = False
    warning: str = ''

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other

    def get_data(self, query_by: str, parameters):
        if query_by == 'bbox':
            query = self.query_by_bbox
        elif query_by == 'id':
            query = self.query_by_id
        else:
            raise ValueError(f'Query by: {query_by} is not valid.')

        data = db.data_from_db(query, parameters, row_as=dict)

        return LayerData(
            len(data),
            [util.input_feature_factory(**row) for row in data]
        )


@dataclass
class LayerData:
    count: int
    data: List[Union[util.InputPoint, util.InputLine, util.InputPolygon]]


class Layers:

    _list_of_layers = [
        LayerDefinition(
            id='addresses_to_import',
            parent_id='addresses',
            name='Adresy brakujące w OSM',
            query_by_id=db.QUERIES['delta_where_id'],
            query_by_bbox=db.QUERIES['delta_where_bbox'],
            export_parameter_name='lb_adresow',
            active=True,
            default=True
        ),
        LayerDefinition(
            id='buildings_to_import',
            parent_id='buildings',
            name='Budynki brakujące w OSM',
            query_by_id=db.QUERIES['buildings_vertices_where_id'],
            query_by_bbox=db.QUERIES['buildings_vertices'],
            export_parameter_name='lb_budynkow',
            active=True,
            default=True
        ),
        LayerDefinition(
            id='addresses',
            parent_id='',
            name='Wszystkie adresy z PRG',
            query_by_id=db.QUERIES['addresses_all_where_id'],
            query_by_bbox=db.QUERIES['addresses_all_where_bbox'],
            export_parameter_name='lb_adresow',
            active=True,
            default=False,
            warning='Nie nadaje się do bezpośredniego importu. ' +
                    'Ta warstwa zawiera wszystkie adresy z PRG na danym obszarze ' +
                    'i służy do podmieniania istniejących w OSM adresów. Dla zaawansowanych edytorów.'
        ),
        LayerDefinition(
            id='buildings',
            parent_id='',
            name='Wszystkie budynki z BDOT10k',
            query_by_id=db.QUERIES['buildings_all_id'],
            query_by_bbox=db.QUERIES['buildings_all_bbox'],
            export_parameter_name='lb_budynkow',
            active=True,
            default=False,
            warning='Nie nadaje się do bezpośredniego importu. ' +
                    'Ta warstwa zawiera wszystkie budynki (z warstwy BUBD) z BDOT10k na danym obszarze ' +
                    'i służy do podmieniania geometrii istniejących w OSM budynków. Dla zaawansowanych edytorów.'
        ),
        LayerDefinition(
            id='streets',
            parent_id='',
            name='Wszystkie ulice z PRG',
            query_by_id=db.QUERIES['streets_all_where_id'],
            query_by_bbox=db.QUERIES['streets_all_where_bbox'],
            export_parameter_name='',
            active=True,
            default=False,
            warning='Nie nadaje się do bezpośredniego importu. ' +
                    'Ta warstwa zawiera wszystkie ulice z PRG na danym obszarze i służy do łatwiejszego dodawania ' +
                    'nowych ulic, ale wymaga uważnego łączenia tych danych z istniejącą w OSM siatką drogową. ' +
                    'Dla zaawansowanych edytorów.'
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

    def selected_layers(self, layer_names: str) -> List[LayerDefinition]:
        """Returns a list of layers matching provided ids (separated by comma). Returns only active layers."""

        if layer_names is None or layer_names == '':
            selected_layers = self.default
        else:
            selected_layers = [
                self._dict_of_layers[str(layer_id).lower().strip()] for layer_id in layer_names.split(',')
                if str(layer_id).lower().strip() in self.active_ids
            ]
            layer_ids = set([x.id for x in selected_layers])
            selected_layers = [layer for layer in selected_layers if layer.parent_id not in layer_ids]

        selected_layers = list(set(selected_layers))  # remove duplicates if any

        return selected_layers


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
        """Returns tuple with object id, dict with tags and dict with geometry."""

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
    """
    Returns proposed addresses within given bounding box. Returns list of instances of ProposedAddress class.
    Proposed addresses are addresses that are present in gov database but are absent from OSM database.
    """

    data = db.data_from_db(db.QUERIES['sc_proposed_addresses_in_bbox'], bbox)
    return [ProposedAddress(*a[:6], json.loads(a[6])) for a in data]


def proposed_addresses_geojson_dict(bbox: Tuple[float, float, float, float]) -> Dict[str, Any]:
    """
    Returns proposed addresses within given bounding box. Returns a dict with the structure of GeoJSON.
    Proposed addresses are addresses that are present in gov database but are absent from OSM database.
    """

    pa = proposed_addresses(bbox)
    data = [x.id_tags_geom_tuple for x in pa]
    features = [util.Feature(id=x[0], tags=x[1], geojson_geometry=x[2]) for x in data]
    return util.to_geojson_dict(features)


def report_addresses(ids: List[str]) -> None:
    """
    Adds address to a list of addresses marked as unsuitable for import. Or more precisely it adds it to a queue.
    After queue entry is processed this address will be removed from the map and won't be returned in future requests.
    """
    db.execute_batch(db.QUERIES['insert_to_exclude_prg'], [(x,) for x in ids])


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
        """Returns tuple with object id, dict with tags and dict with geometry."""

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
    """
    Returns proposed buildings within given bounding box. Returns list of instances of ProposedBuilding class.
    Proposed buildings are buildings that are present in gov database but are absent from OSM database.
    """

    data = db.data_from_db(db.QUERIES['sc_proposed_buildings_in_bbox'], bbox)
    return [ProposedBuilding(*a[:8], json.loads(a[8])) for a in data]


def proposed_buildings_geojson_dict(bbox: Tuple[float, float, float, float]) -> Dict[str, Any]:
    """
    Returns proposed buildings within given bounding box. Returns a dict with the structure of GeoJSON.
    Proposed buildings are buildings that are present in gov database but are absent from OSM database.
    """

    pb = proposed_buildings(bbox)
    data = [x.id_tags_geom_tuple for x in pb]
    features = [util.Feature(id=x[0], tags=x[1], geojson_geometry=x[2]) for x in data]
    return util.to_geojson_dict(features)


def report_buildings(ids: List[str]) -> None:
    """
    Adds building to a list of buildings marked as unsuitable for import. Or more precisely it adds it to a queue.
    After queue entry is processed this building will be removed from the map and won't be returned in future requests.
    """

    db.execute_batch(db.QUERIES['insert_to_exclude_bdot_buildings'], [(x,) for x in ids])
