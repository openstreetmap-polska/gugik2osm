from datetime import datetime, timedelta
from random import choice, random
from typing import Tuple, Dict, List, Union
import json

from flask import request, Response
from flask_restful import Resource, abort
from lxml import etree

from common.database import QUERIES, QueryParametersType, data_from_db, execute_query, execute_batch
import common.util as util
from common.objects import Layers, LayerDefinition, LayerData


class Processes(Resource):
    """Lists processes (data update)."""

    def get(self):
        list_of_processes = data_from_db(QUERIES['processes'])
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


class Exclude(Resource):
    """Endpoint for reporting addresses or buildings that are not fit for import into OSM."""

    def post(self):
        r = request.get_json()

        prg_counter, lod1_counter = 0, 0
        if r.get('prg_ids'):
            prg_ids = [(x,) for x in r['prg_ids']]
            execute_batch(QUERIES['insert_to_exclude_prg'], prg_ids)
            prg_counter = len(prg_ids)
        if r.get('bdot_ids'):
            lod1_ids = [(x,) for x in r['bdot_ids']]
            execute_batch(QUERIES['insert_to_exclude_bdot_buildings'], lod1_ids)
            lod1_counter = len(lod1_ids)

        return {'prg_ids_inserted': prg_counter, 'bdot_ids_inserted': lod1_counter}, 201


class RandomLocation(Resource):
    """Returns random location (lon, lat) while prioritizing (95% chance) areas with a lot of objects to export."""

    def get(self):
        if random() > 0.05:
            query = QUERIES['locations_most_count']
        else:
            query = QUERIES['locations_random']
        list_of_tuples = data_from_db(query)
        x, y = choice(list_of_tuples)
        return {'lon': x, 'lat': y}


class MapboxVectorTile(Resource):
    """Returns vector tile (MVT) with data which can be displayed on the map."""

    def get(self, z: int, x: int, y: int):

        list_of_tuples = data_from_db(QUERIES['cached_mvt'], (z, x, y))
        if len(list_of_tuples) == 0:
            if 6 <= int(z) <= 14:
                execute_query(QUERIES['mvt_insert'], {'z': z, 'x': x, 'y': y})
            else:
                abort(404)
            list_of_tuples = data_from_db(QUERIES['cached_mvt'], (z, x, y))

        mvt = list_of_tuples[0][0] if len(list_of_tuples) == 1 else abort(500)

        # prepare and return response
        response = Response(mvt, status=200, content_type='application/x-protobuf')
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

        list_of_features = [values for layer_id, layer_data in data.items() for values in layer_data.data]
        root = util.create_osm_xml(list_of_features)

        if package_export_params:
            for layer_id, layer_data in data.items():
                if layers[layer_id].export_parameter_name:
                    package_export_params[layers[layer_id].export_parameter_name] = layer_data.count
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

        list_of_features = [values for layer_id, layer_data in data.items() for values in layer_data.data]
        root = util.create_osm_xml(list_of_features)

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=paczka_danych.osm'})

    def register_bbox_export(self, package_export_params: dict) -> None:
        execute_query(QUERIES['insert_to_package_exports'], package_export_params)

    def data_for_layers(self,
                        layers: List[Tuple[LayerDefinition, QueryParametersType]],
                        filter_by: str
                        ) -> Dict[str, LayerData]:
        data = {}

        for layer, params in layers:
            data[layer.id] = layer.get_data(query_by=filter_by, parameters=params)

        return data


class LatestUpdates(Resource):
    """Returns areas that has recently been updated in OSM or areas that were exported as JOSM data package."""

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

        list_of_tuples = data_from_db(QUERIES['latest_updates'], {'ts': ts})
        response_dict = {
            'type': 'FeatureCollection',
            'features': [
                {'type': 'Feature', 'geometry': bbox, 'properties': {'dataset': dataset, 'created_at': created_at}}
                for dataset, created_at, bbox in list_of_tuples
            ]
        }

        # prepare and return response
        expiry_time = ts + timedelta(seconds=60)
        response = Response(
            response=json.dumps(response_dict),
            status=200,
            content_type='application/geo+json',
            headers={
                'X-Accel-Expires': '60',
                'Expires': expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            }
        )

        return response
