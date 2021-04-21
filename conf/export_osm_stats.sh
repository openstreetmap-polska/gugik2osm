#!/bin/bash

# exit on error in any command
set -e

psql -d gugik2osm -f /opt/gugik2osm/conf/gather_osm_stats.sql
psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/osm_stats.sql > /opt/gugik2osm/temp/export/osm_stats.csv
mv /opt/gugik2osm/temp/export/osm_stats.csv /var/www/data/osm_stats.csv
