#!/bin/bash

# exit on error in any command
set -e

psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_msc.sql > /opt/gugik2osm/temp/export/teryt_msc.csv
mv /opt/gugik2osm/temp/export/teryt_msc.csv /var/www/data/teryt_msc.csv
