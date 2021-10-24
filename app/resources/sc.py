import json

from flask import request, Response
from flask_restful import Resource, abort

from common.objects import addresses, buildings


class ProposedAddresses(Resource):

    def get(self):

        min_lon = request.args.get('xmin')
        min_lat = request.args.get('ymin')
        max_lon = request.args.get('xmax')
        max_lat = request.args.get('ymax')

        if not all([min_lon, min_lat, max_lon, max_lat]):
            abort(400)

        min_lon = float(min_lon)
        min_lat = float(min_lat)
        max_lon = float(max_lon)
        max_lat = float(max_lat)

        geojson_dict = addresses.proposed_addresses_geojson_dict((min_lon, min_lat, max_lon, max_lat))

        return Response(
            json.dumps(geojson_dict),
            mimetype='application/geo+json',
            headers={'Access-Control-Allow-Origin': '*'}
        )


class ReportProposedAddress(Resource):

    def post(self):
        """Expects body with a list of addresses ids."""

        parsed_request = request.get_json()
        if parsed_request:
            addresses.report_addresses(parsed_request)
        else:
            abort(400)

        return 'OK'


class ProposedBuildings(Resource):

    def get(self):

        min_lon = request.args.get('xmin')
        min_lat = request.args.get('ymin')
        max_lon = request.args.get('xmax')
        max_lat = request.args.get('ymax')

        if not all([min_lon, min_lat, max_lon, max_lat]):
            abort(400)

        min_lon = float(min_lon)
        min_lat = float(min_lat)
        max_lon = float(max_lon)
        max_lat = float(max_lat)

        geojson_dict = buildings.proposed_buildings_geojson_dict((min_lon, min_lat, max_lon, max_lat))

        return Response(
            json.dumps(geojson_dict),
            mimetype='application/geo+json',
            headers={'Access-Control-Allow-Origin': '*'}
        )


class ReportProposedBuilding(Resource):

    def post(self):
        """Expects body with a list of buildings ids."""

        parsed_request = request.get_json()
        if parsed_request:
            buildings.report_buildings(parsed_request)
        else:
            abort(400)

        return 'OK'
