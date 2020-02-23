#!/bin/bash

source /opt/gugik2osm/conf/.env

date >> /opt/gugik2osm/log/prg_processing.log
python3.7 -u /opt/gugik2osm/git/processing/scripts/prg_prepare.py --full --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
date >> /opt/gugik2osm/log/prg_processing.log
