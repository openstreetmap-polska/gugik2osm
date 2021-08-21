from os import environ

from flask_restful import Api
from flask import Flask

from resources.internal import (JosmData, MapboxVectorTile, RandomLocation, Exclude, Processes, LatestUpdates,
                                AvailableLayers, MarkTileForReload)
from resources.sc import ProposedAddresses, ReportProposedAddress, ProposedBuildings, ReportProposedBuilding

app = Flask(__name__)
api = Api(app)

api.add_resource(JosmData, '/josm_data')
api.add_resource(AvailableLayers, '/layers/')
api.add_resource(MapboxVectorTile, '/tiles/<int:z>/<int:x>/<int:y>.pbf')
api.add_resource(MarkTileForReload, '/tiles/<int:z>/<int:x>/<int:y>/reload')
api.add_resource(RandomLocation, '/random/')
api.add_resource(Exclude, '/exclude/')
api.add_resource(Processes, '/processes/')
api.add_resource(LatestUpdates, '/updates.geojson')

api.add_resource(ProposedAddresses, '/sc/proposed_addresses')
api.add_resource(ReportProposedAddress, '/sc/proposed_addresses/report')
api.add_resource(ProposedBuildings, '/sc/proposed_buildings')
api.add_resource(ReportProposedBuilding, '/sc/proposed_buildings/report')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=environ.get('flask_debug', False))
