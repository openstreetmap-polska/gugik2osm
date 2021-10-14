import unittest

import lxml.etree
from lxml import etree

from app.common import util


class ConversionToOSMObjectsTests(unittest.TestCase):

    def test_creating_node(self):
        point = util.InputPoint(tags={}, latitude=0.1, longitude=0.3)
        nodes, ways, relations = util.convert_to_osm_style_objects([point])
        assert len(nodes) == 1
        assert len(ways) == 0
        assert len(relations) == 0
        node = nodes[0]
        assert node.id == -1
        assert node.latitude == 0.1
        assert node.longitude == 0.3

    def test_creating_two_nodes(self):
        point1 = util.InputPoint(tags={}, latitude=0.1, longitude=0.3)
        point2 = util.InputPoint(tags={}, latitude=1, longitude=1)
        nodes, ways, relations = util.convert_to_osm_style_objects([point1, point2])
        assert len(nodes) == 2
        assert len(ways) == 0
        assert len(relations) == 0

    def test_node_with_tags(self):
        point = util.InputPoint(tags={'test': 'test'}, latitude=0, longitude=0)
        nodes, ways, relations = util.convert_to_osm_style_objects([point])
        node = nodes[0]
        assert node.tags == {'test': 'test'}

    def test_node_without_tags(self):
        point = util.InputPoint(tags={}, latitude=0, longitude=0)
        nodes, ways, relations = util.convert_to_osm_style_objects([point])
        node = nodes[0]
        assert node.tags == {}

    def test_creating_way_from_line(self):
        line_coordinates = [(0, 0), (1, 1), (2, 2)]
        line = util.InputLine(tags={}, list_of_coordinate_pairs=line_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([line])
        assert len(nodes) == 3
        assert len(ways) == 1
        assert len(relations) == 0
        way = ways[0]
        assert len(way.node_ids) == 3
        nodes_dict = {n.id: (n.latitude, n.longitude) for n in nodes}
        reconstructed_line_coordinates = [nodes_dict[node_id] for node_id in way.node_ids]
        assert len(reconstructed_line_coordinates) == 3
        assert line_coordinates == reconstructed_line_coordinates

    def test_way_with_tags(self):
        line_coordinates = [(0, 0), (1, 1), (2, 2)]
        line = util.InputLine(tags={'test': 'test'}, list_of_coordinate_pairs=line_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([line])
        way = ways[0]
        assert way.tags == {'test': 'test'}

    def test_way_without_tags(self):
        line_coordinates = [(0, 0), (1, 1), (2, 2)]
        line = util.InputLine(tags={}, list_of_coordinate_pairs=line_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([line])
        way = ways[0]
        assert way.tags == {}

    def test_creating_way_from_polygon(self):
        polygon_coordinates = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        polygon = util.InputPolygon(tags={}, outer_ring=polygon_coordinates, inner_rings=[])
        nodes, ways, relations = util.convert_to_osm_style_objects([polygon])
        assert len(nodes) == 4  # one node is reused
        assert len(ways) == 1
        assert len(relations) == 0
        way = ways[0]
        assert len(way.node_ids) == 5
        nodes_dict = {n.id: (n.latitude, n.longitude) for n in nodes}
        reconstructed_polygon_coordinates = [nodes_dict[node_id] for node_id in way.node_ids]
        assert len(reconstructed_polygon_coordinates) == 5
        assert polygon_coordinates == reconstructed_polygon_coordinates

    def test_creating_relation_from_donut_polygon(self):
        outer_ring_coordinates = [(0.3, 0.3), (0, 10), (10, 10), (10, 0), (0.3, 0.3)]
        inner_ring_coordinates = [[(3.3, 3.3), (4, 4), (4, 3), (3.3, 3.3)]]
        polygon = util.InputPolygon(tags={}, outer_ring=outer_ring_coordinates, inner_rings=inner_ring_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([polygon])
        assert len(nodes) == 7  # two nodes are reused
        assert len(ways) == 2
        assert len(relations) == 1
        relation = relations[0]
        assert len(relation.members) == 2
        nodes_dict = {n.id: (n.latitude, n.longitude) for n in nodes}
        outer_ring = [member for member in relation.members if member.role == 'outer'][0]
        inner_ring = [member for member in relation.members if member.role == 'inner'][0]
        outer_nodes = [way for way in ways if way.id == outer_ring.id][0].node_ids
        reconstructed_outer_ring = [nodes_dict[node_id] for node_id in outer_nodes]
        assert len(reconstructed_outer_ring) == 5
        assert outer_ring_coordinates == reconstructed_outer_ring
        inner_nodes = [way for way in ways if way.id == inner_ring.id][0].node_ids
        reconstructed_inner_ring = [[nodes_dict[node_id] for node_id in inner_nodes]]
        assert len(reconstructed_inner_ring) == 1
        assert len(reconstructed_inner_ring[0]) == 4
        assert inner_ring_coordinates == reconstructed_inner_ring

    def test_creating_relation_from_multipolygon(self):
        outer_rings_coordinates = [[(0.3, 0.3), (0, 10), (10, 10), (10, 0), (0.3, 0.3)], [(20, 20), (20, 30), (30, 30), (30, 20), (20, 20)]]
        inner_ring_coordinates = [[(3.3, 3.3), (4, 4), (4, 3), (3.3, 3.3)]]
        multipolygon = util.InputMultiPolygon(tags={}, outer_rings=outer_rings_coordinates, inner_rings=inner_ring_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([multipolygon])
        assert len(nodes) == 11  # two nodes are reused
        assert len(ways) == 3
        assert len(relations) == 1
        relation = relations[0]
        assert len(relation.members) == 3
        outer_rings = [member for member in relation.members if member.role == 'outer']
        assert len(outer_rings) == 2

    def test_relation_with_tags(self):
        outer_ring_coordinates = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
        inner_ring_coordinates = [[(3, 3), (4, 4), (4, 3), (3, 3)]]
        polygon = util.InputPolygon(tags={'test': 'test'}, outer_ring=outer_ring_coordinates, inner_rings=inner_ring_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([polygon])
        # 'type': 'multipolygon' is always added
        assert relations[0].tags == {'type': 'multipolygon', 'test': 'test'}

    def test_relation_without_tags(self):
        outer_ring_coordinates = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
        inner_ring_coordinates = [[(3, 3), (4, 4), (4, 3), (3, 3)]]
        polygon = util.InputPolygon(tags={}, outer_ring=outer_ring_coordinates, inner_rings=inner_ring_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([polygon])
        # 'type': 'multipolygon' is always added
        assert relations[0].tags == {'type': 'multipolygon'}

    def test_creating_many_objects(self):
        # create point
        point = util.InputPoint(tags={'point': 'yes'}, latitude=0, longitude=0)
        # create line
        line_coordinates = [(0, 0), (1, 1), (2, 2)]
        line = util.InputLine(tags={'line': 'yes'}, list_of_coordinate_pairs=line_coordinates)
        # create polygon
        outer_ring_coordinates = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
        inner_ring_coordinates = [[(3, 3), (4, 4), (4, 3), (3, 3)]]
        polygon = util.InputPolygon(tags={}, outer_ring=outer_ring_coordinates, inner_rings=inner_ring_coordinates)

        nodes, ways, relations = util.convert_to_osm_style_objects([point, line, polygon])
        assert len(nodes) == 9
        assert len(ways) == 3
        assert len(relations) == 1

        assert len([n for n in nodes if n.tags.get('point')]) == 1

        way = [w for w in ways if w.tags.get('line')][0]
        assert len(way.node_ids) == 3
        nodes_dict = {n.id: (n.latitude, n.longitude) for n in nodes}
        reconstructed_line_coordinates = [nodes_dict[node_id] for node_id in way.node_ids]
        assert len(reconstructed_line_coordinates) == 3
        assert line_coordinates == reconstructed_line_coordinates

        relation = relations[0]
        assert len(relation.members) == 2
        nodes_dict = {n.id: (n.latitude, n.longitude) for n in nodes}
        outer_ring = [member for member in relation.members if member.role == 'outer'][0]
        inner_ring = [member for member in relation.members if member.role == 'inner'][0]
        outer_nodes = [way for way in ways if way.id == outer_ring.id][0].node_ids
        reconstructed_outer_ring = [nodes_dict[node_id] for node_id in outer_nodes]
        assert len(reconstructed_outer_ring) == 5
        assert outer_ring_coordinates == reconstructed_outer_ring
        inner_nodes = [way for way in ways if way.id == inner_ring.id][0].node_ids
        reconstructed_inner_ring = [[nodes_dict[node_id] for node_id in inner_nodes]]
        assert len(reconstructed_inner_ring) == 1
        assert len(reconstructed_inner_ring[0]) == 4
        assert inner_ring_coordinates == reconstructed_inner_ring

    def test_node_tag_merging(self):
        point1 = util.InputPoint(tags={'p': 1}, latitude=0, longitude=0)
        point2 = util.InputPoint(tags={'point': 'no'}, latitude=0, longitude=0)
        point3 = util.InputPoint(tags={'point': 'yes', 'pp': 2}, latitude=0, longitude=0)

        nodes, ways, relations = util.convert_to_osm_style_objects([point1, point2, point3])
        assert len(nodes) == 1
        assert len(ways) == 0
        assert len(relations) == 0
        assert nodes[0].tags == {'p': 1, 'point': 'yes', 'pp': 2}


class ConversionToXMLTests(unittest.TestCase):

    def test_with_one_node(self):
        point = util.InputPoint(tags={}, latitude=0.1, longitude=1.3)
        nodes, ways, relations = util.convert_to_osm_style_objects([point])
        node = nodes[0]
        xml = node.as_xml_element()
        assert xml.tag == 'node'
        assert len(list(xml)) == 0
        assert xml.get('lat') == '0.1'
        assert xml.get('lon') == '1.3'
        assert xml.get('id') == '-1'

    def test_with_two_nodes(self):
        point1 = util.InputPoint(tags={}, latitude=0.1, longitude=1.3)
        point2 = util.InputPoint(tags={'key1': 'value1', 'key2': 'value2'}, latitude=0, longitude=1)
        nodes, ways, relations = util.convert_to_osm_style_objects([point1, point2])
        node1 = [n for n in nodes if n.latitude == 0.1 and n.longitude == 1.3][0]
        node2 = [n for n in nodes if n.latitude == 0 and n.longitude == 1][0]
        xml1 = node1.as_xml_element()
        xml2 = node2.as_xml_element()
        assert len(list(xml1)) == 0
        assert len(list(xml2)) == 2
        assert xml2[0].tag == 'tag'
        assert xml2[0].get('k') == 'key1'
        assert xml2[0].get('v') == 'value1'
        assert xml2[1].tag == 'tag'
        assert xml2[1].get('k') == 'key2'
        assert xml2[1].get('v') == 'value2'

    def test_with_two_intersecting_nodes(self):
        point1 = util.InputPoint(tags={}, latitude=0.1, longitude=1.3)
        point2 = util.InputPoint(tags={'key1': 'value1', 'key2': 'value2'}, latitude=0.1, longitude=1.3)
        nodes, ways, relations = util.convert_to_osm_style_objects([point1, point2])
        node = nodes[0]
        xml = node.as_xml_element()
        tags = {child.get('k'): child.get('v') for child in xml}
        assert xml.tag == 'node'
        assert len(list(xml)) == 2
        assert xml.get('lat') == '0.1'
        assert xml.get('lon') == '1.3'
        assert xml.get('id') == '-1'
        assert tags['key1'] == 'value1'
        assert tags['key2'] == 'value2'

    def test_with_one_line(self):
        line_coordinates = [(0, 0), (1, 1), (2, 2)]
        line = util.InputLine(tags={'test': 'test'}, list_of_coordinate_pairs=line_coordinates)
        nodes, ways, relations = util.convert_to_osm_style_objects([line])
        way = ways[0]
        xml = way.as_xml_element()
        tags = {child.get('k'): child.get('v') for child in xml if child.tag == 'tag'}
        nodes_references = [child for child in xml if child.tag == 'nd']
        assert xml.tag == 'way'
        assert len(list(xml)) == 4
        assert len(nodes_references) == 3
        assert tags['test'] == 'test'

    def test_with_two_lines(self):
        pass

    def test_with_two_intersecting_lines(self):
        pass

    def test_with_one_simple_polygon(self):
        pass

    def test_with_two_simple_polygons(self):
        pass

    def test_with_one_donut_polygon(self):
        pass

    def test_with_one_donut_polygon_with_many_holes(self):
        pass

    def test_with_one_simple_multipolygon(self):
        pass

    def test_with_one_donut_multipolygon(self):
        pass

    def test_with_one_node_one_intersecting_line(self):
        pass

    def test_with_one_node_one_line_one_polygon(self):
        pass


if __name__ == "__main__":
    unittest.main()
