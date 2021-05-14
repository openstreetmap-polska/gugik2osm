#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_gmi.sql > /opt/gugik2osm/temp/export/teryt_gmi.csv
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/teryt_gmi.csv teryt_gmi.csv
rm /opt/gugik2osm/temp/export/teryt_gmi.csv
