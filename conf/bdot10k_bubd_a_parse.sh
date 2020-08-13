#!/bin/bash

source /opt/gugik2osm/conf/.env

date >> /opt/gugik2osm/log/bdot_processing.log
echo "Processing BDOT files..." >> /opt/gugik2osm/log/bdot_processing.log
python3.7 -u /opt/gugik2osm/git/processing/parsers/bdot10k.py --input /opt/gugik2osm/tempbdot/BDOT10k_*.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" --prep_tables --basic_fields --create_lookup_tables --create_view >> /opt/gugik2osm/log/bdot_processing.log 2>&1
date >> /opt/gugik2osm/log/bdot_processing.log
