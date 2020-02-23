#!/bin/bash 

source /opt/gugik2osm/conf/.env

date >> /opt/gugik2osm/log/teryt_processing.log
python3.7 -u /opt/gugik2osm/git/processing/scripts/teryt_dl.py --api_env prod --api_user "$TERYTUSER" --api_password "$TERYTPASSWORD" --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/teryt_processing.log 2>&1
date >> /opt/gugik2osm/log/teryt_processing.log
