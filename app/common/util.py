import logging
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Union, Dict, Any, Tuple
from lxml import etree


BUILDING_TAG = etree.Element('tag', k='building', v='yes')
SOURCE_BUILDING = etree.Element('tag', k='source', v='www.geoportal.gov.pl')
SOURCE_ADDR = etree.Element('tag', k='source:addr', v='gugik.gov.pl')

XMLElementType = Union[etree.ElementTree, etree.Element]


def prepare_xml_tree(root: etree.Element, children: List[XMLElementType]) -> etree.ElementTree:
    for child in children:
        root.append(child)
    return root


def addresses_nodes(list_of_tuples: list) -> etree.Element:
    i = -1  # counter for fake ids
    for t in list_of_tuples:
        el = etree.Element('node', id=str(i), lat=str(t[8]), lon=str(t[7]))
        el.append(deepcopy(SOURCE_ADDR))
        # do not add 'ref:addr' tag
        # el.append(etree.Element('tag', k='ref:addr', v=t[0]))
        el.append(etree.Element('tag', k='addr:city:simc', v=t[2]))
        if t[3]:
            el.append(etree.Element('tag', k='addr:city', v=t[1]))
            el.append(etree.Element('tag', k='addr:street', v=t[3]))
            # do not add TERYT ULIC code
            # el.append(etree.Element('tag', k='addr:street:sym_ul', v=t[4]))
        else:
            el.append(etree.Element('tag', k='addr:place', v=t[1]))
        el.append(etree.Element('tag', k='addr:housenumber', v=t[5]))
        if t[6]:
            el.append(etree.Element('tag', k='addr:postcode', v=t[6]))
        i -= 1
        yield el


def buildings_nodes(list_of_tuples: list) -> etree.Element:
    i = -100000  # counter for fake ids
    n = {}  # list of nodes
    lst = []  # list of ways
    # cursor returns tuple of (way_id, array_of_points[])
    for t in list_of_tuples:
        # create 'way' node for xml tree
        way = etree.Element('way', id=str(t[0]))
        way.append(deepcopy(SOURCE_BUILDING))

        if t[2]:
            way.append(etree.Element('tag', k='building', v=t[2]))
        if t[3]:
            way.append(etree.Element('tag', k='amenity', v=t[3]))
        if t[4]:
            way.append(etree.Element('tag', k='man_made', v=t[4]))
        if t[5]:
            way.append(etree.Element('tag', k='leisure', v=t[5]))
        if t[6]:
            way.append(etree.Element('tag', k='historic', v=t[6]))
        if t[7]:
            way.append(etree.Element('tag', k='tourism', v=t[7]))
        if t[8]:
            way.append(etree.Element('tag', k='building:levels', v=str(t[8])))

        # iterate over array of points that make the polygon and add references to them to the way xml node
        for xy in t[1]:
            # if given point is already in our list of nodes then:
            if n.get(tuple(xy)):
                way.append(deepcopy(n[tuple(xy)]['el']))
                # appending doesn't work when you try to pass the same object
                # you need to create new object if you want nodes with duplicate values
                # since polygons start and end with the same node we need to deepcopy the object
            else:
                temp = etree.Element('nd', ref=str(i))
                way.append(temp)
                n[tuple(xy)] = {'el': temp, 'id': i}
            i -= 1
        lst.append(way)

    for k, v in n.items():
        yield etree.Element('node', id=str(v['id']), lat=str(k[1]), lon=str(k[0]))

    for w in lst:
        yield w


def addresses_xml(list_of_tuples):
    """Method creates XML with address points in OSM schema."""
    root = etree.Element('osm', version='0.6')
    i = -1  # counter for fake ids
    for t in list_of_tuples:
        el = etree.Element('node', id=str(i), lat=str(t[8]), lon=str(t[7]))
        el.append(deepcopy(SOURCE_ADDR))
        # do not add 'ref:addr' tag
        # el.append(etree.Element('tag', k='ref:addr', v=t[0]))
        el.append(etree.Element('tag', k='addr:city:simc', v=t[2]))
        if t[3]:
            el.append(etree.Element('tag', k='addr:city', v=t[1]))
            el.append(etree.Element('tag', k='addr:street', v=t[3]))
            # do not add TERYT ULIC code
            # el.append(etree.Element('tag', k='addr:street:sym_ul', v=t[4]))
        else:
            el.append(etree.Element('tag', k='addr:place', v=t[1]))
        el.append(etree.Element('tag', k='addr:housenumber', v=t[5]))
        if t[6]:
            el.append(etree.Element('tag', k='addr:postcode', v=t[6]))
        root.append(el)
        i -= 1
    return root


def buildings_xml(list_of_tuples):
    """Method creates XML with buildings (polygons) in OSM schema."""
    root = etree.Element('osm', version='0.6')
    i = -1  # counter for fake ids
    n = {}  # list of nodes
    lst = []  # list of ways
    # cursor returns tuple of (way_id, array_of_points[])
    for t in list_of_tuples:
        # create 'way' node for xml tree
        way = etree.Element('way', id=str(t[0]))
        way.append(deepcopy(SOURCE_BUILDING))

        if t[2]:
            way.append(etree.Element('tag', k='building', v=t[2]))
        if t[3]:
            way.append(etree.Element('tag', k='amenity', v=t[3]))
        if t[4]:
            way.append(etree.Element('tag', k='man_made', v=t[4]))
        if t[5]:
            way.append(etree.Element('tag', k='leisure', v=t[5]))
        if t[6]:
            way.append(etree.Element('tag', k='historic', v=t[6]))
        if t[7]:
            way.append(etree.Element('tag', k='tourism', v=t[7]))
        if t[8]:
            way.append(etree.Element('tag', k='building:levels', v=str(t[8])))

        # iterate over array of points that make the polygon and add references to them to the way xml node
        for xy in t[1]:
            # if given point is already in our list of nodes then:
            if n.get(tuple(xy)):
                way.append(deepcopy(n[tuple(xy)]['el']))
                # appending doesn't work when you try to pass the same object
                # you need to create new object if you want nodes with duplicate values
                # since polygons start and end with the same node we need to deepcopy the object
            else:
                temp = etree.Element('nd', ref=str(i))
                way.append(temp)
                n[tuple(xy)] = {'el': temp, 'id': i}
            i -= 1
        lst.append(way)

    for k, v in n.items():
        root.append(etree.Element('node', id=str(v['id']), lat=str(k[1]), lon=str(k[0])))

    for w in lst:
        root.append(w)

    return root


@dataclass
class Feature:
    id: str
    tags: Dict[str, Any]
    geojson_geometry: Dict[str, Any]


def to_geojson_dict(features: List[Feature]) -> Dict[str, Any]:
    results = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': feature.geojson_geometry,
                'properties': {
                    'id': feature.id,
                    'tags': feature.tags
                }
            }
            for feature in features
        ]
    }
    return results


@dataclass
class InputPoint:
    tags: Dict[str, Any]
    latitude: float
    longitude: float


@dataclass
class InputLine:
    tags: Dict[str, Any]
    list_of_coordinate_pairs: List[Tuple[float, float]]


@dataclass
class InputPolygon:
    tags: Dict[str, Any]
    outer_ring: List[Tuple[float, float]]
    inner_rings: List[List[Tuple[float, float]]]


@dataclass
class Node:
    id: int
    tags: Dict[str, Any]
    latitude: float
    longitude: float

    def as_xml_element(self) -> etree.Element:
        tags_elements = [etree.Element('tag', k=key, v=str(value)) for key, value in self.tags.items()]
        node_element = etree.Element('node', id=str(self.id), lat=str(self.latitude), lon=str(self.longitude))
        for elem in tags_elements:
            node_element.append(elem)
        return node_element


@dataclass
class Way:
    id: int
    tags: Dict[str, Any]
    node_ids: List[int]

    def as_xml_element(self) -> etree.Element:
        tags_elements = [etree.Element('tag', k=key, v=str(value)) for key, value in self.tags.items()]
        node_id_elements = [etree.Element('nd', ref=str(node_id)) for node_id in self.node_ids]
        way_element = etree.Element('way', id=str(self.id))
        for elem in node_id_elements:
            way_element.append(elem)
        for elem in tags_elements:
            way_element.append(elem)
        return way_element


@dataclass
class RelationMember:
    type: str
    id: int
    role: str

    def as_xml_element(self) -> etree.Element:
        return etree.Element('member', type=self.type, ref=str(self.id), role=self.role)


@dataclass
class Relation:
    id: int
    tags: Dict[str, Any]
    members: List[RelationMember]

    def as_xml_element(self) -> etree.Element:
        tags_elements = [etree.Element('tag', k=key, v=str(value)) for key, value in self.tags.items()]
        member_elements = [member.as_xml_element() for member in self.members]
        relation_element = etree.Element('relation', id=str(self.id))
        for elem in member_elements:
            relation_element.append(elem)
        for elem in tags_elements:
            relation_element.append(elem)
        return relation_element


class DecreasingSequence:
    def __init__(self, starting_value: int = -1, step: int = -1):
        self.value = starting_value
        if step == 0:
            raise ValueError('Step cannot be equal zero.')
        if step > 0:
            logging.warning('DecreasingSequence given step greater than zero. Sequence will increase instead of decreasing.')
        self.step = step

    def next_value(self):
        self.value += self.step
        return self.value


def trim_coordinates(lat: float, lon: float) -> Tuple[float, float]:
    return round(lat, 7), round(lon, 7)


def input_feature_factory(geom_type: str, **kwargs) -> Union[InputPoint, InputLine, InputPolygon]:

    if geom_type == 'POINT':
        feature = InputPoint(tags=kwargs['tags'], latitude=kwargs['latitude'], longitude=kwargs['longitude'])
    elif geom_type == 'LINESTRING':
        feature = InputLine(tags=kwargs['tags'], list_of_coordinate_pairs=kwargs['list_of_coordinate_pairs'])
    elif geom_type == 'POLYGON':
        feature = InputPolygon(tags=kwargs['tags'], outer_ring=kwargs['outer_ring'], inner_rings=kwargs['inner_rings'])
    else:
        raise AttributeError(f'Geometry type: {geom_type} currently not supported.')

    return feature


def convert_to_osm_style_objects(
        list_of_features: List[Union[InputPoint, InputLine, InputPolygon]]
) -> Tuple[List[Node], List[Way], List[Relation]]:
    """"Method converts """

    node_id_seq = DecreasingSequence()
    way_id_seq = DecreasingSequence()
    relation_id_seq = DecreasingSequence()

    list_of_nodes = []
    node_dict = {}
    list_of_ways = []
    list_of_relations = []

    def create_way(list_of_coordinates: List[Tuple[float, float]], tags: Dict[str, Any]) -> int:
        node_ids = []
        for coordinates in list_of_coordinates:
            lat_lon_tuple = trim_coordinates(*coordinates)
            if node_dict.get(lat_lon_tuple):
                node_id = node_dict.get(lat_lon_tuple)
            else:
                new_node = Node(node_id_seq.next_value(), {}, *lat_lon_tuple)
                node_id = new_node.id
                node_dict[lat_lon_tuple] = node_id
                list_of_nodes.append(new_node)
            node_ids.append(node_id)

        w = Way(way_id_seq.next_value(), tags, node_ids)
        list_of_ways.append(w)
        return w.id

    expected_classes = [InputPoint, InputLine, InputPolygon]
    for feature in list_of_features:
        if isinstance(feature, InputPoint):
            lat, lon = trim_coordinates(feature.latitude, feature.longitude)

            if node_dict.get((lat, lon)):
                logging.warning(f'Node with coordinates {lat}, {lon} already exists in dictionary. Skipping.')
                continue

            n = Node(node_id_seq.next_value(), feature.tags, lat, lon)
            node_dict[(lat, lon)] = n.id
            list_of_nodes.append(n)

        elif isinstance(feature, InputLine):
            create_way(feature.list_of_coordinate_pairs, feature.tags)

        elif isinstance(feature, InputPolygon):
            if len(feature.inner_rings) == 0:
                # create way
                create_way(feature.outer_ring, feature.tags)
            else:
                # create a relation
                outer_id = create_way(feature.outer_ring, dict())
                inner_ids = [create_way(ring, dict()) for ring in feature.inner_rings]
                members = [RelationMember('way', outer_id, 'outer')] + [RelationMember('way', i, 'inner') for i in inner_ids]
                relation_tags = {**feature.tags, 'type': 'multipolygon'}
                r = Relation(relation_id_seq.next_value(), relation_tags, members)
                list_of_relations.append(r)

        else:
            raise ValueError(f'Feature is not one of expected types: {type(feature)}. Expected one of: {expected_classes}')

    return list_of_nodes, list_of_ways, list_of_relations


def create_osm_xml(list_of_features: List[Union[InputPoint, InputLine, InputPolygon]]) -> etree.Element:
    """Method """

    root = etree.Element('osm', version='0.6')
    list_of_nodes, list_of_ways, list_of_relations = convert_to_osm_style_objects(list_of_features)
    for node in list_of_nodes:
        root.append(node)
    for way in list_of_ways:
        root.append(way)
    for relation in list_of_relations:
        root.append(relation)

    return root
