#!/bin/bash

source /opt/gugik2osm/conf/.env

python3 -u /opt/gugik2osm/git/processing/scripts/expired_tiles.py --insert-exp-tiles --dir /opt/gugik2osm/imposm3/exptiles/ --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/data_update.log 2>&1
python3 -u /opt/gugik2osm/git/processing/scripts/prg_prepare.py --update --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/data_update.log 2>&1

