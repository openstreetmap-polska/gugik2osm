from os import environ

from flask_restful import Api
from flask import Flask

from resources.internal import (JosmData, PrgAddressesNotInOSM, BuildingsNotInOSM, MapboxVectorTile, AddressPointInfo,
                                RandomLocation, Excluded, Processes, LatestUpdates)

app = Flask(__name__)
api = Api(app)

api.add_resource(JosmData, '/josm_data')
api.add_resource(PrgAddressesNotInOSM, '/prg/not_in/osm/')
api.add_resource(BuildingsNotInOSM, '/lod1/not_in/osm/')
api.add_resource(MapboxVectorTile, '/tiles/<int:z>/<int:x>/<int:y>.pbf')
api.add_resource(AddressPointInfo, '/delta/<string:uuid>/')
api.add_resource(RandomLocation, '/random/')
api.add_resource(Excluded, '/exclude/')
api.add_resource(Processes, '/processes/')
api.add_resource(LatestUpdates, '/updates.geojson')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=environ.get('flask_debug', False))
