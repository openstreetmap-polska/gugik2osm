#!/bin/bash

# expiretiles-zoom is added due to bug in imposm3: https://github.com/omniscale/imposm3/issues/181
/opt/gugik2osm/imposm3/imposm-0.11.1-linux-x86-64/imposm run -config /opt/gugik2osm/imposm3/config.json -expiretiles-zoom 18
