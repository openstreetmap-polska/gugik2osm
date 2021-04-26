from copy import deepcopy
from dataclasses import dataclass
from typing import List, Union, Dict, Any
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
