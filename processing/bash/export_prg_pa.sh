#!/usr/bin/env bash

# exit on error in any command
set -e

psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/prg_pa.sql > /opt/gugik2osm/temp/export/prg_pa.csv
zip -9 -j /opt/gugik2osm/temp/export/prg_pa.zip /opt/gugik2osm/temp/export/prg_pa.csv
mv /opt/gugik2osm/temp/export/prg_pa.zip /var/www/data/prg_pa.zip
rm /opt/gugik2osm/temp/export/prg_pa.csv
