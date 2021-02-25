from dataclasses import dataclass
from typing import Callable, List, Dict

from .database import QUERIES
from .util import addresses_nodes, buildings_nodes


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
        # LayerDefinition(
        #     id='addresses',
        #     name='Wszystkie adresy z PRG',
        #     query_by_id=QUERIES['delta_where_id'],
        #     query_by_bbox=QUERIES['delta_where_bbox'],
        #     convert_to_xml_element=addresses_nodes,
        #     export_parameter_name='lb_adresow',
        #     active=False,
        #     default=False,
        #     warning='Dla zaawansowanych edytorów. ' +
        #             'Ta warstwa zawiera wszystkie adresy z PRG na danym obszarze i nie nadaje się do bezpośredniego ' +
        #             'importu. Używaj z rozwagą.'
        # ),
        LayerDefinition(
            id='buildings',
            name='Wszystkie budynki z BDOT10k',
            query_by_id=QUERIES['buildings_all_id'],
            query_by_bbox=QUERIES['buildings_all_bbox'],
            convert_to_xml_element=buildings_nodes,
            export_parameter_name='lb_budynkow',
            active=False,
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
