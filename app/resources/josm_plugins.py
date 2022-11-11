import json

from flask import request, Response
from flask_restful import Resource, abort

from lxml import etree

from common import util, objects
from common.objects import addresses, buildings


class NearestBuilding(Resource):

    def get(self):
        """
        Returns the nearest building within search distance of given coordinates.
        Query automatically limits search distance to 0.005 degree regardless of parameters.
        If search_distance_in_meters is not provided it is set to 30m.
        """

        lon = request.args.get('lon')
        lat = request.args.get('lat')
        search_distance = request.args.get('search_distance')

        if not all([lon, lat]):
            abort(400)

        try:
            lon = float(lon)
            lat = float(lat)
            if search_distance:
                search_distance = float(search_distance)
            else:
                search_distance = 30.0
        except ValueError:
            abort(400)

        list_of_features = buildings.nearest_building_josm_xml(
            lat=lat,
            lon=lon,
            search_distance_in_meters=search_distance,
        )
        number_of_buildings = len(list_of_features)
        root = util.create_osm_xml(list_of_features)

        if number_of_buildings > 0:
            geojson_geometry_string = buildings.nearest_building_geom_only(
                lat=lat,
                lon=lon,
                search_distance_in_meters=search_distance,
            )[0]
            objects.layers.register_export(
                geojson_geometry=geojson_geometry_string,
                lb_adresow=0,
                lb_budynkow=number_of_buildings,
            )

        return Response(
            etree.tostring(root, encoding='UTF-8'),
            mimetype='text/xml',
        )


class NearestBuildingGeojson(Resource):

    def get(self):
        """
        Returns the nearest building within search distance of given coordinates.
        Query automatically limits search distance to 0.005 degree regardless of parameters.
        If search_distance_in_meters is not provided it is set to 30m.
        """

        lon = request.args.get('lon')
        lat = request.args.get('lat')
        search_distance = request.args.get('search_distance')

        if not all([lon, lat]):
            abort(400)

        try:
            lon = float(lon)
            lat = float(lat)
            if search_distance:
                search_distance = float(search_distance)
            else:
                search_distance = 30.0
        except ValueError:
            abort(400)

        geojson_dict = buildings.nearest_building_josm_geojson(
            lat=lat,
            lon=lon,
            search_distance_in_meters=search_distance,
        )
        number_of_buildings = len(geojson_dict["features"])

        if number_of_buildings > 0:
            geojson_geometry_string = json.dumps(geojson_dict["features"][0]["geometry"])
            objects.layers.register_export(
                geojson_geometry=geojson_geometry_string,
                lb_adresow=0,
                lb_budynkow=number_of_buildings,
            )

        return Response(
            json.dumps(geojson_dict),
            mimetype='application/geo+json',
        )
