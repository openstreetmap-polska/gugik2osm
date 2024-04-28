#!/usr/bin/env bash

# exit on error in any command
set -e

psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_woj.sql > /opt/gugik2osm/temp/export/teryt_woj.csv
mv /opt/gugik2osm/temp/export/teryt_woj.csv /var/www/data/teryt_woj.csv
