#!/bin/bash

source /opt/gugik2osm/conf/.env

echo "Deploying buildings categories mappings..." >> /opt/gugik2osm/log/prg_processing.log

psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -f /opt/gugik2osm/git/processing/sql/ddl/bdot_buildings_osm_tags_mappings.sql >> /opt/gugik2osm/log/prg_processing.log 2>&1
cat /opt/gugik2osm/git/processing/sql/data/buildings_categories_mappings.csv | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy bdot.buildings_categories_mappings FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1

echo "Done." >> /opt/gugik2osm/log/prg_processing.log
