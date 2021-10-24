import re
from datetime import datetime, timedelta
import json

from flask import request, Response
from flask_restful import Resource, abort
from lxml import etree

from common import util
from common import objects


class Processes(Resource):
    """Lists processes (data update)."""

    def get(self):
        list_of_processes = objects.processes.status()
        return {'processes': [p.as_dict() for p in list_of_processes]}


class Exclude(Resource):
    """Endpoint for reporting addresses or buildings that are not fit for import into OSM."""

    def post(self):
        r = request.get_json()
        exclude_prg_addresses = r.get('exclude_prg_addresses')
        exclude_bdot_buildings = r.get('exclude_bdot_buildings')
        geojson_geometry_string = r.get('geom')

        if geojson_geometry_string:
            if exclude_prg_addresses:
                objects.addresses.report_addresses_in_polygon(geojson_geometry_string)
            if exclude_bdot_buildings:
                objects.buildings.report_buildings_in_polygon(geojson_geometry_string)
            return {}, 201
        else:
            # keep old path for compatibility
            prg_counter, lod1_counter = 0, 0
            if r.get('prg_ids'):
                prg_ids = r['prg_ids']
                objects.addresses.report_addresses(prg_ids)
                prg_counter = len(prg_ids)
            if r.get('bdot_ids'):
                bdot_ids = r['bdot_ids']
                objects.buildings.report_buildings(bdot_ids)
                lod1_counter = len(bdot_ids)

            return {'prg_ids_inserted': prg_counter, 'bdot_ids_inserted': lod1_counter}, 201


class RandomLocation(Resource):
    """Returns random location (lon, lat) while prioritizing (95% chance) areas with a lot of objects to export."""

    def get(self):
        point = objects.locations.random_location()
        return {'lon': point.longitude, 'lat': point.latitude}


class MapboxVectorTile(Resource):
    """Returns vector tile (MVT) with data which can be displayed on the map."""

    def get(self, z: int, x: int, y: int):

        tile = objects.tiles.select(z, x, y)
        if tile is None:
            if 6 <= int(z) <= 14:
                objects.tiles.generate_if_not_exists(z, x, y)
            else:
                abort(404)
            tile = objects.tiles.select(z, x, y)

        mvt = tile.data if tile is not None else abort(500)

        # prepare and return response
        response = Response(mvt, status=200, content_type='application/x-protobuf')
        if 6 <= int(z) < 9:
            response.headers['X-Accel-Expires'] = '120'
        elif 10 <= int(z) < 23:
            response.headers['X-Accel-Expires'] = '60'
        return response


class MarkTileForReload(Resource):
    """Marks MVT to be reloaded with next data update."""

    def get(self, z: int, x: int, y: int):
        objects.tiles.queue_for_reload(z, x, y)
        return 'OK', 201


class AvailableLayers(Resource):
    """Provides list of ids of available layers with data to download."""

    def get(self):
        return {
            'available_layers': objects.layers.Layers().active_ids_with_names
        }


class JosmData(Resource):
    """Returns data for given area as an osm file."""

    def get(self):
        geojson_geometry_string = ''
        layers = objects.layers.Layers()

        selected_layers = layers.selected_layers(request.args.get('layers', ''))
        if len(selected_layers) == 0:
            abort(400)

        if request.args.get('filter_by') == 'bbox':
            bbox = (
                float(request.args.get('xmin')), float(request.args.get('ymin')),
                float(request.args.get('xmax')), float(request.args.get('ymax'))
            )
            geojson_geometry_string = json.dumps(util.bbox_to_geojson_geometry(bbox))
        elif request.args.get('filter_by') == 'geojson_geometry':
            geojson_geometry_string = request.args.get('geom')
            # todo: validate geometry
        elif request.args.get('filter_by') == 'osm_boundary':
            if request.args.get('teryt_terc') and re.match(r'^\d{2,7}$', request.args.get('teryt_terc')):
                terc = request.args.get('teryt_terc')
                geojson_geometry_string = objects.osm_admin_boundaries.select_where_terc(terc_code=terc)[0].value
            elif request.args.get('teryt_simc') and re.match(r'^\d{7}$', request.args.get('teryt_simc')):
                simc = request.args.get('teryt_simc')
                geojson_geometry_string = objects.osm_admin_boundaries.select_where_simc(simc_code=simc)[0].value
            elif request.args.get('relation_id') and re.match(r'^\d+$', request.args.get('relation_id')):
                relation_id = int(request.args.get('relation_id'))
                geojson_geometry_string = objects.osm_admin_boundaries.select_where_id(relation_id=relation_id)[0].value
            else:
                abort(400)
        else:
            abort(400)

        data = objects.layers.select_data_for_layers([(layer, {'geojson_geometry': geojson_geometry_string}) for layer in selected_layers])

        list_of_features = [values for layer_id, layer_data in data.items() for values in layer_data.data]
        root = util.create_osm_xml(list_of_features)

        package_export_params = {'geojson_geometry': geojson_geometry_string}
        for layer_id, layer_data in data.items():
            if layers[layer_id].export_parameter_name:
                package_export_params[layers[layer_id].export_parameter_name] = layer_data.count
        required_parameters = ['lb_adresow', 'lb_budynkow']
        for param in required_parameters:
            if package_export_params.get(param) is None:
                package_export_params[param] = 0
        objects.layers.register_export(**package_export_params)

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=paczka_danych.osm'})


class LatestUpdates(Resource):
    """Returns areas that has recently been updated in OSM or areas that were exported as JOSM data package."""

    def get(self):
        ts = request.args.get('after')
        if ts is None:
            ts = datetime.now() - timedelta(minutes=60)
        else:
            try:
                ts = datetime.fromisoformat(ts)
            except:
                abort(400)
        if ts - datetime.now() > timedelta(hours=24, minutes=5):
            abort(400)

        list_of_updates = objects.updates.latest_updates(ts)
        list_of_geometries = [u.area for u in list_of_updates]
        list_of_properties = [
            {'dataset': u.dataset, 'created_at': u.created_at, 'changesets': u.changesets} for u in list_of_updates
        ]
        response_dict = util.create_geojson_dict(list_of_geometries, list_of_properties)

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
