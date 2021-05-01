#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

psql -d gugik2osm -f /opt/gugik2osm/conf/gather_osm_stats.sql
psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/osm_stats.sql > /opt/gugik2osm/temp/export/osm_stats.csv
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/osm_stats.csv osm_stats.csv
mv /opt/gugik2osm/temp/export/osm_stats.csv /var/www/data/osm_stats.csv
