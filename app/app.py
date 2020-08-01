from os import environ

from flask_restful import Api
from flask import Flask

from resources.internal import JosmData, PrgAddressesNotInOSM, Lod1LegalInfo, Lod1BuildingsNotInOSM, MapboxVectorTile, \
    AddressPointInfo, RandomLocation, Excluded, Processes

app = Flask(__name__)
api = Api(app)


api.add_resource(JosmData, '/josm_data')
api.add_resource(PrgAddressesNotInOSM, '/prg/not_in/osm/')
api.add_resource(Lod1LegalInfo, '/lod1/not_in/osm/info.json')
api.add_resource(Lod1BuildingsNotInOSM, '/lod1/not_in/osm/')
api.add_resource(MapboxVectorTile, '/tiles/<int:z>/<int:x>/<int:y>.pbf')
api.add_resource(AddressPointInfo, '/delta/<string:uuid>/')
api.add_resource(RandomLocation, '/random/')
api.add_resource(Excluded, '/exclude/')
api.add_resource(Processes, '/processes/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=environ.get('flask_debug', False))
