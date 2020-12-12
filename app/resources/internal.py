import io
from random import choice, random
from os import environ
from typing import Tuple, Optional

from flask import request, Response
from flask_restful import Resource, abort
import requests as requests_lib
from lxml import etree

from common.database import pgdb, execute_sql, QUERIES, execute_values, pg
from common.util import to_merc, Tile, bounds, buildings_xml, notes, addresses_xml, addresses_nodes, buildings_nodes


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
    """Endpoint for reporting addresses or buildings that are not fit for import into OSM. Requires captcha token."""
    def post(self):
        r = request.get_json()
        captcha_user_token = request.headers.get('reCaptchaUserToken')
        # verify if request is correct
        if captcha_user_token is None:
            abort(400)
        if r is None:
            raise ValueError(request.form)
        if r is None or (r.get('prg_ids') is None and r.get('lod1_ids') is None):
            abort(400)
        # verify captcha token
        response = requests_lib.post(
            url='https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': environ.get('reCaptchaSecretToken'),
                'response': captcha_user_token
            }
        )
        if not(response.ok and response.json().get('success')):
            abort(400)

        conn = pgdb()
        with conn.cursor() as cur:
            prg_counter, lod1_counter = 0, 0
            if r.get('prg_ids'):
                prg_ids = [(x,) for x in r['prg_ids']]
                execute_values(cur, QUERIES['insert_to_exclude_prg'], prg_ids)
                prg_counter = len(prg_ids)
            if r.get('lod1_ids'):
                lod1_ids = [(x,) for x in r['lod1_ids']]
                execute_values(cur, QUERIES['insert_to_exclude_lod1'], lod1_ids)
                lod1_counter = len(lod1_ids)
            conn.commit()
        return {'prg_ids_inserted': prg_counter, 'lod1_ids_inserted': lod1_counter}, 201


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
        # calculate bbox
        tile = Tile(x, y, z)
        bbox = to_merc(bounds(tile))

        # query db
        conn = pgdb()
        cur = execute_sql(conn.cursor(), QUERIES['cached_mvt'], (z, x, y))
        tup = cur.fetchone()
        if tup is None:
            params = {
                'xmin': bbox['west'],
                'ymin': bbox['south'],
                'xmax': bbox['east'],
                'ymax': bbox['north'],
                'z': z,
                'x': x,
                'y': y
            }
            if 6 <= int(z) <= 7:
                cur = execute_sql(cur, QUERIES['mvt_ll_aggr_terc'], params)
            elif 8 <= int(z) <= 9:
                cur = execute_sql(cur, QUERIES['mvt_ll_aggr_simc'], params)
            elif 10 <= int(z) <= 11:
                cur = execute_sql(cur, QUERIES['mvt_ll_aggr_simc_ulic'], params)
            elif 12 <= int(z) <= 12:
                cur = execute_sql(cur, QUERIES['mvt_ll'], params)
            elif 13 <= int(z) < 23:
                cur = execute_sql(cur, QUERIES['mvt_hl'], params)
            else:
                abort(404)
            conn.commit()
            cur = execute_sql(cur, QUERIES['cached_mvt'], (z, x, y))
            tup = cur.fetchone()
        mvt = io.BytesIO(tup[0]).getvalue() if tup else abort(500)

        # prepare and return response
        response = Response(mvt)
        response.headers['Content-Type'] = 'application/x-protobuf'
        response.headers['Access-Control-Allow-Origin'] = "*"
        cur.close()
        if 6 <= int(z) < 13:
            response.headers['X-Accel-Expires'] = '10800'
        elif 13 <= int(z) < 23:
            response.headers['X-Accel-Expires'] = '60'
        return response


class JosmData(Resource):
    """Newer version of the function returning data as osm file with the new endpoint."""

    def get(self):
        addresses_query, buildings_query = self.queries()
        addresses_params, buildings_params = None, None
        root = etree.Element('osm', version='0.6')
        if request.args.get('filter_by') == 'bbox':
            addresses_params = (float(request.args.get('xmin')),
                                float(request.args.get('ymin')),
                                float(request.args.get('xmax')),
                                float(request.args.get('ymax')))
            buildings_params = addresses_params
        elif request.args.get('filter_by') == 'id':
            temp1 = request.args.get('addresses_ids')
            addresses_params = (tuple(temp1.split(',')),) if temp1 else None  # tuple of tuples was needed
            temp2 = request.args.get('buildings_ids')
            buildings_params = (tuple(temp2.split(',')),) if temp2 else None  # tuple of tuples was needed

        a, b = self.data(addresses_query, addresses_params, buildings_query, buildings_params)
        root = self.prepare_xml_tree(root, a, b)

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=paczka_danych.osm'})

    def post(self):
        if request.args.get('filter_by') != 'id':
            abort(400)

        addresses_query, buildings_query = self.queries()
        root = etree.Element('osm', version='0.6')

        temp = request.get_json()
        temp1 = temp.get('addresses_ids')
        temp2 = temp.get('buildings_ids')
        addresses_params = (tuple(temp1),) if temp1 and len(temp1) > 0 else None
        buildings_params = (tuple(temp2),) if temp2 and len(temp2) > 0 else None

        a, b = self.data(addresses_query, addresses_params, buildings_query, buildings_params)
        root = self.prepare_xml_tree(root, a, b)

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=paczka_danych.osm'})

    def data(self, addresses_query, addresses_params, buildings_query, buildings_params):
        addresses, buildings = [], []
        with pgdb().cursor() as cur:
            if addresses_query and addresses_params and len(addresses_params) > 0:
                cur = execute_sql(cur, addresses_query, addresses_params)
                addresses = cur.fetchall()

            if buildings_query and buildings_params and len(buildings_params) > 0:
                cur = execute_sql(cur, buildings_query, buildings_params)
                buildings = cur.fetchall()

        return addresses, buildings

    def prepare_xml_tree(self, root, addresses, buildings):
        for an in addresses_nodes(addresses):
            root.append(an)
        for bn in buildings_nodes(buildings):
            root.append(bn)
        return root

    def queries(self) -> Tuple[Optional[str], Optional[str]]:
        if request.args.get('filter_by') == 'bbox':
            if not (
                    'xmin' in request.args and 'xmax' in request.args
                    and
                    'ymin' in request.args and 'ymax' in request.args
            ):
                abort(400)
        if request.args.get('filter_by') not in {'bbox', 'id'}:
            abort(400)

        addresses_query, buildings_query = None, None
        if request.args.get('filter_by') == 'bbox':
            addresses_query = QUERIES['delta_where_bbox']
            buildings_query = QUERIES['buildings_vertices']
        elif request.args.get('filter_by') == 'id':
            addresses_query = QUERIES['delta_where_id']
            buildings_query = QUERIES['buildings_vertices_where_id']

        return addresses_query, buildings_query


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


class Lod1LegalInfo(Resource):
    def get(self):
        return notes


class Lod1BuildingsNotInOSM(Resource):
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
