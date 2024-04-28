#!/usr/bin/env bash

# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

echo "Deploying buildings categories mappings..." >> /opt/gugik2osm/log/prg_processing.log

psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "truncate table bdot.buildings_categories_mappings" >> /opt/gugik2osm/log/prg_processing.log 2>&1
cat /opt/gugik2osm/git/processing/sql/data/buildings_categories_mappings.csv | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy bdot.buildings_categories_mappings FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1

echo "Done." >> /opt/gugik2osm/log/prg_processing.log
