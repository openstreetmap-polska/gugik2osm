#!/bin/bash
#source /opt/gugik2osm/conf/.env
# for some reason using source .env doesn't work here so the variables with user/password etc. are created locally
# these need to be updated before deploy

PGDATABASE=""
PGHOSTADDR="127.0.0.1"
PGPORT="5432"
PGUSER=""
PGPASSWORD=""

DSN="postgis://$PGUSER:$PGPASSWORD@$PGHOSTADDR:$PGPORT/$PGDATABASE"

/opt/gugik2osm/imposm3/imposm-0.10.0-linux-x86-64/imposm run -mapping /opt/gugik2osm/imposm3/mapping.yaml -cachedir /opt/gugik2osm/imposm3/cache/ -connection "$DSN" -limitto /opt/gugik2osm/imposm3/poland.geojson -srid 4326 -expiretiles-dir /opt/gugik2osm/imposm3/exptiles/ -expiretiles-zoom 18
