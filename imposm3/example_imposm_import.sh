#!/bin/bash

/opt/gugik2osm/imposm3/imposm-0.11.0-linux-x86-64/imposm import -mapping /opt/gugik2osm/imposm3/mapping.yaml -read /opt/gugik2osm/imposm3/poland-latest.osm.pbf -overwritecache -cachedir /opt/gugik2osm/imposm3/cache/ -connection postgis://<user>:<password>@localhost:5432/<db_name> -limitto /opt/gugik2osm/imposm3/poland.geojson -srid 4326 -write -diff -deployproduction
