#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_pow.sql > /opt/gugik2osm/temp/export/teryt_pow.csv
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/teryt_pow.csv teryt_pow.csv
rm /opt/gugik2osm/temp/export/teryt_pow.csv
