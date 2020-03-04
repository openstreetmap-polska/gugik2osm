import io
from copy import deepcopy
from os import environ
from lxml import etree
import psycopg2 as pg
from flask import Flask, request, abort, Response, jsonify
from sql import *
import mercantile as m
from pyproj import Proj, transform
from typing import Union
from datetime import datetime, timezone
from os.path import join, dirname, abspath
from random import random, choice


SQL_PATH = join(dirname(abspath(__file__)), 'queries')
QUERIES = {
    'buildings_vertices': str(open(join(SQL_PATH, 'buildings_vertices.sql'), 'r').read()),
    'cached_mvt': str(open(join(SQL_PATH, 'cached_mvt.sql'), 'r').read()),
    'delta_point_info': str(open(join(SQL_PATH, 'delta_point_info.sql'), 'r').read()),
    'delta_where_bbox': str(open(join(SQL_PATH, 'delta_where_bbox.sql'), 'r').read()),
    'mvt_hl': str(open(join(SQL_PATH, 'mvt_hl.sql'), 'r').read()),
    'mvt_ll': str(open(join(SQL_PATH, 'mvt_ll.sql'), 'r').read()),
    'locations_random': str(open(join(SQL_PATH, 'locations_random.sql'), 'r').read()),
    'locations_most_count': str(open(join(SQL_PATH, 'locations_most_count.sql'), 'r').read()),
}
conn = None
app = Flask(__name__)


def pgdb():
    """Method returns connection to the DB. If there is no connection active it creates one."""
    global conn
    if conn:
        return conn
    else:
        conn = pg.connect(dsn=environ['dsn'])
        return conn


def execute_sql(cursor, query: str, parameters: Union[tuple, dict] = None):
    """Method executes SQL query in a given cursor with given parameters. Provides error handling.
    In case of exception it rolls back transaction and closes the connection."""
    try:
        cursor.execute(query, parameters) if parameters else cursor.execute(query)
    except:
        global conn
        print(datetime.now(timezone.utc).astimezone().isoformat(),
              f'- Error while executing query: {query}, with parameters: {parameters}')
        conn.rollback()
        conn.close()
        conn = None
        raise
    return cursor


def to_merc(bbox: m.LngLatBbox) -> dict:
    in_proj = Proj('epsg:4326')
    out_proj = Proj('epsg:3857')
    res = dict()
    res["west"], res["south"] = transform(in_proj, out_proj, bbox.south, bbox.west)
    res["east"], res["north"] = transform(in_proj, out_proj, bbox.north, bbox.east)
    return res


@app.route('/prg/not_in/osm/', methods=['GET'])
def features_in():
    if request.args.get('filter_by') == 'bbox':
        if not (
                'xmin' in request.args and 'xmax' in request.args
                and
                'ymin' in request.args and 'ymax' in request.args
        ):
            abort(400)

    cur = execute_sql(
        pgdb().cursor(),
        sql_where_bbox,
        (float(request.args.get('xmin')),
         float(request.args.get('ymin')),
         float(request.args.get('xmax')),
         float(request.args.get('ymax')))
    )

    if request.args.get('format') == 'osm':
        root = etree.Element('osm', version='0.6')
        i = -1  # counter for fake ids
        for t in cur:
            el = etree.Element('node', id=str(i), lat=str(t[8]), lon=str(t[7]))
            el.append(deepcopy(SOURCE_ADDR))
            el.append(etree.Element('tag', k='ref:addr', v=t[0]))
            el.append(etree.Element('tag', k='addr:city:simc', v=t[2]))
            if t[3]:
                el.append(etree.Element('tag', k='addr:city', v=t[1]))
                el.append(etree.Element('tag', k='addr:street', v=t[3]))
                el.append(etree.Element('tag', k='addr:street:sym_ul', v=t[4]))
            else:
                el.append(etree.Element('tag', k='addr:place', v=t[1]))
            el.append(etree.Element('tag', k='addr:housenumber', v=t[5]))
            if t[6]:
                el.append(etree.Element('tag', k='addr:postcode', v=t[6]))
            root.append(el)
            i -= 1

        # etree.ElementTree(root).write(fpath, encoding='UTF-8')
        cur.close()
        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=prg_addresses.osm'})
    elif request.args.get('format') == 'json':
        d = {
            'features': [
                {'lokalnyid': x[0], 'miejscowosc': x[1], 'simc': x[2], 'ulica': x[3], 'teryt_ulic': x[4], 'nr': x[5],
                 'pna': x[6], 'longitude': x[7], 'latitude': x[8]} for x in cur
            ]
        }
        cur.close()
        return jsonify(d)
    else:
        abort(400)


notes = {
    'zbior': 'Modele 3D Budynków',
    'zrodlo': 'www.geoportal.gov.pl',
    'dysponent': 'Główny Geodeta Kraju',
    'data_pobrania_zbioru': '2019-11-10',
    'zakres_przetworzenia': 'Geometria budynków została spłaszczona do 2D oraz wyekstrahowana została część poligonowa wykorzystana dalej jako obrys budynku.',
    'informacja': '''Modele 3D budynków nie stanowią rejestru publicznego ani elementu treści takiego rejestru. W konsekwencji czego mają wartość jedynie poglądową. Niezgodność Modeli 3D budynków ze stanem faktycznym lub prawnym, tak w postaci nieprzetworzonej jak i po ich ewentualnym przetworzeniu w procesie ponownego wykorzystania, nie może stanowić podstawy odpowiedzialności Głównego Geodety Kraju z jakiegokolwiek tytułu wobec jakiegokolwiek podmiotu.''',
    'licencja': r'https://integracja.gugik.gov.pl/Budynki3D/GUGiK_Licencja_na_Budynki3D.pdf'
}
bld = etree.Element('tag', k='building', v='yes')
src = etree.Element('tag', k='source', v='www.geoportal.gov.pl')
SOURCE_ADDR = etree.Element('tag', k='source:addr', v='gugik.gov.pl')


@app.route('/lod1/not_in/osm/info.json', methods=['GET'])
def buildings_info():
    return jsonify(notes)


@app.route('/lod1/not_in/osm/', methods=['GET'])
def buildings():
    if request.args.get('filter_by') == 'bbox':
        if not (
                'xmin' in request.args and 'xmax' in request.args
                and
                'ymin' in request.args and 'ymax' in request.args
        ):
            abort(400)
    else:
        abort(400)

    cur = execute_sql(
        pgdb().cursor(),
        sql_buildings_where_bbox,
        (float(request.args.get('xmin')), float(request.args.get('ymin')),
         float(request.args.get('xmax')), float(request.args.get('ymax')))
    )

    if request.args.get('format') == 'osm':
        root = etree.Element('osm', version='0.6')
        i = -1  # counter for fake ids
        n = {}  # list of nodes
        lst = []  # list of ways
        # cursor returns tuple of (way_id, array_of_points[])
        for t in cur:
            # create 'way' node for xml tree
            way = etree.Element('way', id=str(t[0]))
            way.append(deepcopy(bld))
            way.append(deepcopy(src))

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

        cur.close()
        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
            headers={'Content-disposition': 'attachment; filename=buildings.osm'})
    else:
        abort(400)


@app.route("/tiles/<int:z>/<int:x>/<int:y>.pbf")
def tile_server(z, x, y):
    # calculate bbox
    tile = m.Tile(x, y, z)
    bbox = to_merc(m.bounds(tile))

    # query db
    cur = execute_sql(pgdb().cursor(), sql_get_mvt_by_zxy, (z, x, y))
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
        if 6 <= int(z) < 13:
            cur = execute_sql(cur, sql_mvt_ll, params)
        elif 13 <= int(z) < 23:
            cur = execute_sql(cur, sql_mvt, params)
        else:
            abort(404)
        conn.commit()
        tup = cur.fetchone()
    mvt = io.BytesIO(tup[0]).getvalue() if tup else b''

    # prepare and return response
    response = app.make_response(mvt)
    response.headers['Content-Type'] = 'application/x-protobuf'
    response.headers['Access-Control-Allow-Origin'] = "*"
    cur.close()
    return response


@app.route('/prg/<uuid>')
def prg_address_point_info(uuid: str):
    cur = execute_sql(pgdb().cursor(), sql_delta_point_info, (uuid,))
    info = cur.fetchone()
    cur.close()
    if info:
        return jsonify(
            {
                'lokalnyid': info[0], 'teryt_msc': info[1], 'teryt_simc': info[2],
                'teryt_ulica': info[3], 'teryt_ulic': info[4], 'nr': info[5], 'pna': info[6]
            })
    else:
        return jsonify({'Error': f'Address point with lokalnyid(uuid): {uuid} not found.'}), 404


@app.route('/random/')
def random_location():
    if random() > 0.1:
        query = QUERIES['locations_most_count']
    else:
        query = QUERIES['locations_random']
    cur = execute_sql(pgdb().cursor(), query)
    x, y = choice(cur.fetchall())
    cur.close()
    return jsonify({'lon': x, 'lat': y})


if __name__ == '__main__':
    app.run()
