import io
from datetime import datetime, timedelta
from random import choice, random
from typing import Tuple, Dict, List
import json

from flask import request, Response
from flask_restful import Resource, abort
from lxml import etree

from common.database import pgdb, execute_sql, QUERIES, execute_values, pg, QueryParametersType, QueryOutputType
from common.util import buildings_xml, addresses_xml, XMLElementType
import common.util as util
from common.objects import Layers, LayerDefinition


class Processes(Resource):
    """Lists processes (data update)."""
    def get(self):
        cur = execute_sql(pgdb().cursor(), QUERIES['processes'])
        list_of_processes = cur.fetchall()
        result = {
            'processes': [
                {
                    'name': x[0], 'in_progress': x[1], 'start_time': x[2], 'end_time': x[3],
                    'no_of_tiles_to_process': x[4], 'abbr_name': x[5], 'last_status': x[6]
                }
                for x in list_of_processes
            ]
        }
        return result


class Excluded(Resource):
    """Endpoint for reporting addresses or buildings that are not fit for import into OSM."""
    def post(self):
        r = request.get_json()

        conn = pgdb()
        with conn.cursor() as cur:
            prg_counter, lod1_counter = 0, 0
            if r.get('prg_ids'):
                prg_ids = [(x,) for x in r['prg_ids']]
                execute_values(cur, QUERIES['insert_to_exclude_prg'], prg_ids)
                prg_counter = len(prg_ids)
            if r.get('bdot_ids'):
                lod1_ids = [(x,) for x in r['bdot_ids']]
                execute_values(cur, QUERIES['insert_to_exclude_bdot_buildings'], lod1_ids)
                lod1_counter = len(lod1_ids)
            conn.commit()
        return {'prg_ids_inserted': prg_counter, 'bdot_ids_inserted': lod1_counter}, 201


class RandomLocation(Resource):
    """Returns random location (lon, lat) while prioritizing areas with a lot of objects to export."""
    def get(self):
        if random() > 0.1:
            query = QUERIES['locations_most_count']
        else:
            query = QUERIES['locations_random']
        with pgdb().cursor() as cur:
            execute_sql(cur, query)
            x, y = choice(cur.fetchall())
        return {'lon': x, 'lat': y}


class AddressPointInfo(Resource):
    def get(self, uuid: str):
        with pgdb().cursor() as cur:
            try:
                cur = execute_sql(cur, QUERIES['delta_point_info'], (uuid,))
            except pg.errors.InvalidTextRepresentation:
                return {'Error': f'Error parsing string: `{uuid}` to UUID.'}, 400
            info = cur.fetchone()

        if info:
            return {'lokalnyid': info[0], 'teryt_msc': info[1], 'teryt_simc': info[2],
                    'teryt_ulica': info[3], 'teryt_ulic': info[4], 'nr': info[5], 'pna': info[6]}
        else:
            return {'Error': f'Address point with lokalnyid(uuid): {uuid} not found.'}, 404


class MapboxVectorTile(Resource):
    def get(self, z: int, x: int, y: int):

        # query db
        conn = pgdb()
        cur = execute_sql(conn.cursor(), QUERIES['cached_mvt'], (z, x, y))
        tup = cur.fetchone()
        if tup is None:
            if 6 <= int(z) <= 14:
                cur = execute_sql(cur, QUERIES['mvt_insert'], {'z': z, 'x': x, 'y': y})
            else:
                abort(404)
            conn.commit()
            cur = execute_sql(cur, QUERIES['cached_mvt'], (z, x, y))
            tup = cur.fetchone()
        mvt = io.BytesIO(tup[0]).getvalue() if tup else abort(500)

        # prepare and return response
        response = Response(mvt)
        response.headers['Content-Type'] = 'application/x-protobuf'
        cur.close()
        if 6 <= int(z) < 9:
            response.headers['X-Accel-Expires'] = '120'
        elif 10 <= int(z) < 23:
            response.headers['X-Accel-Expires'] = '60'
        return response


class AvailableLayers(Resource):
    """Provides list of ids of available layers with data to download."""

    def get(self):
        return {
            'available_layers': Layers().active_ids_with_names
        }


class JosmData(Resource):
    """Newer version of the function returning data as osm file with the new endpoint."""

    def get(self):
        package_export_params = None
        root = etree.Element('osm', version='0.6')
        layers = Layers()

        data = {}
        if request.args.get('filter_by') == 'bbox':
            selected_layers = layers.selected_layers(request.args.get('layers', ''))
            if len(selected_layers) == 0:
                abort(400)
            bbox = (
                float(request.args.get('xmin')), float(request.args.get('ymin')),
                float(request.args.get('xmax')), float(request.args.get('ymax'))
            )
            package_export_params = {'xmin': bbox[0], 'ymin': bbox[1], 'xmax': bbox[2], 'ymax': bbox[3]}
            data = self.data_for_layers([(layer, bbox) for layer in selected_layers], 'bbox')
        elif request.args.get('filter_by') == 'id':
            selected_layers_and_params = []
            temp1 = request.args.get('addresses_ids')
            addresses_params = (tuple(temp1.split(',')),) if temp1 else None  # tuple of tuples was needed
            if addresses_params:
                selected_layers_and_params.append((layers['addresses_to_import'], addresses_params))
            temp2 = request.args.get('buildings_ids')
            buildings_params = (tuple(temp2.split(',')),) if temp2 else None  # tuple of tuples was needed
            if buildings_params:
                selected_layers_and_params.append((layers['buildings_to_import'], buildings_params))
            data = self.data_for_layers(selected_layers_and_params, 'id')
        elif request.args.get('filter_by') == 'geom_wkt':
            # not implemented yet
            abort(400)
        else:
            abort(400)

        xml_children = []
        for k, v in data.items():
            xml_children.extend(v['data'])
            if package_export_params and layers[k].export_parameter_name:
                package_export_params[layers[k].export_parameter_name] = v['count']
        root = util.prepare_xml_tree(root, xml_children)

        if package_export_params:
            required_parameters = ['lb_adresow', 'lb_budynkow']
            for param in required_parameters:
                if package_export_params.get(param) is None:
                    package_export_params[param] = 0
            self.register_bbox_export(package_export_params)

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=paczka_danych.osm'})

    def post(self):
        if request.args.get('filter_by') != 'id':
            abort(400)

        root = etree.Element('osm', version='0.6')
        layers = Layers()

        temp = request.get_json()
        temp1 = temp.get('addresses_ids')
        temp2 = temp.get('buildings_ids')
        addresses_params = (tuple(temp1),) if temp1 and len(temp1) > 0 else None
        buildings_params = (tuple(temp2),) if temp2 and len(temp2) > 0 else None

        selected_layers_and_params = []
        if addresses_params:
            selected_layers_and_params.append((layers['addresses_to_import'], addresses_params))
        if buildings_params:
            selected_layers_and_params.append((layers['buildings_to_import'], buildings_params))

        data = self.data_for_layers(selected_layers_and_params, 'id')
        xml_children = []
        for k, v in data.items():
            xml_children.extend(v['data'])
        root = util.prepare_xml_tree(root, xml_children)

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=paczka_danych.osm'})

    def register_bbox_export(self, package_export_params: dict) -> None:
        conn = pgdb()
        with conn.cursor() as cur:
            cur.execute(QUERIES['insert_to_package_exports'], package_export_params)
            conn.commit()

    def data_for_layers(self, layers: List[Tuple[LayerDefinition, QueryParametersType]], filter_by: str) -> Dict[str, XMLElementType]:
        data = {}

        with pgdb().cursor() as cur:
            for layer, params in layers:
                if filter_by == 'bbox':
                    query = layer.query_by_bbox
                elif filter_by == 'id':
                    query = layer.query_by_id
                else:
                    raise NotImplementedError()
                cur = execute_sql(cur, query, params)
                temp = cur.fetchall()
                data[layer.id] = {
                    'count': len(temp),
                    'data': layer.convert_to_xml_element(temp)
                }

        return data


class PrgAddressesNotInOSM(Resource):
    def get(self):
        if request.args.get('filter_by') == 'bbox':
            if not (
                    'xmin' in request.args and 'xmax' in request.args
                    and
                    'ymin' in request.args and 'ymax' in request.args
            ):
                abort(400)
        if request.args.get('format') not in {'osm', 'xml'}:
            abort(400)

        with pgdb().cursor() as cur:
            execute_sql(
                cur,
                QUERIES['delta_where_bbox'],
                (float(request.args.get('xmin')),
                 float(request.args.get('ymin')),
                 float(request.args.get('xmax')),
                 float(request.args.get('ymax')))
            )
            root = addresses_xml(cur.fetchall())

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=prg_addresses.osm'})


class BuildingsNotInOSM(Resource):
    def get(self):
        if request.args.get('filter_by') == 'bbox':
            if not (
                    'xmin' in request.args and 'xmax' in request.args
                    and
                    'ymin' in request.args and 'ymax' in request.args
            ):
                abort(400)
        else:
            abort(400)
        if request.args.get('format') not in {'osm', 'xml'}:
            abort(400)

        with pgdb().cursor() as cur:
            execute_sql(
                cur,
                QUERIES['buildings_vertices'],
                (float(request.args.get('xmin')), float(request.args.get('ymin')),
                 float(request.args.get('xmax')), float(request.args.get('ymax')))
            )
            root = buildings_xml(cur.fetchall())

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=buildings.osm'})


class LatestUpdates(Resource):
    def get(self):
        ts = request.args.get('after')
        if ts is None:
            ts = datetime.now() - timedelta(minutes=120)
        else:
            try:
                ts = datetime.fromisoformat(ts)
            except:
                abort(400)
        if ts - datetime.now() > timedelta(hours=24, minutes=5):
            abort(400)

        with pgdb().cursor() as cur:
            execute_sql(
                cur,
                QUERIES['latest_updates'],
                {'ts': ts}
            )
            data = cur.fetchall()
        response_dict = {
            'type': 'FeatureCollection',
            'features': [
                {'type': 'Feature', 'geometry': bbox, 'properties': {'dataset': dataset, 'created_at': created_at}}
                for dataset, created_at, bbox in data
            ]
        }

        # prepare and return response
        response = Response(json.dumps(response_dict))
        response.headers['Content-Type'] = 'application/geo+json'
        response.headers['X-Accel-Expires'] = '60'

        return response
