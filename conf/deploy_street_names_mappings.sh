#!/bin/bash

source /opt/gugik2osm/conf/.env

echo "Deploying street names mappings..." >> /opt/gugik2osm/log/prg_processing.log

psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -f /opt/gugik2osm/git/processing/sql/ddl/street_names_mappings.sql >> /opt/gugik2osm/log/prg_processing.log 2>&1
cat /opt/gugik2osm/git/processing/sql/data/street_names_mappings.csv | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy street_names_mappings FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1

echo "Done." >> /opt/gugik2osm/log/prg_processing.log
