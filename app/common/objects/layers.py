from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from .. import util
from .. import database as db


@dataclass(frozen=True)
class LayerDefinition:
    id: str
    parent_id: str
    name: str
    query: str
    export_parameter_name: str
    active: bool = True
    default: bool = False
    warning: str = ''

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other

    def get_data(self, geometry):

        data = db.data_from_db(self.query, geometry, row_as=dict)
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
            query=db.QUERIES['addresses_where_geom'],
            export_parameter_name='lb_adresow',
            active=True,
            default=True
        ),
        LayerDefinition(
            id='buildings_to_import',
            parent_id='buildings',
            name='Budynki brakujące w OSM',
            query=db.QUERIES['buildings_where_geom'],
            export_parameter_name='lb_budynkow',
            active=True,
            default=True
        ),
        LayerDefinition(
            id='addresses',
            parent_id='',
            name='Wszystkie adresy z PRG',
            query=db.QUERIES['addresses_all_where_geom'],
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
            query=db.QUERIES['buildings_all_where_geom'],
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
            query=db.QUERIES['streets_all_where_geom'],
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


def select_data_for_layers(layers: List[Tuple[LayerDefinition, db.QueryParametersType]]) -> Dict[str, LayerData]:
    data = {}
    for layer, params in layers:
        data[layer.id] = layer.get_data(params)

    return data


def register_export(geojson_geometry: str, lb_adresow: int, lb_budynkow: int) -> None:
    db.execute_query(
        db.QUERIES['insert_to_package_exports'],
        {'geojson_geometry': geojson_geometry, 'lb_adresow': lb_adresow, 'lb_budynkow': lb_budynkow}
    )
