#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/osm_addresses.sql > /opt/gugik2osm/temp/export/osm_addresses.csv
zip -9 -j /opt/gugik2osm/temp/export/osm_addresses.zip /opt/gugik2osm/temp/export/osm_addresses.csv
rm /opt/gugik2osm/temp/export/osm_addresses.csv
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/osm_addresses.zip osm_addresses.zip
rm /opt/gugik2osm/temp/export/osm_addresses.zip
