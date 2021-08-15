#!/bin/bash

# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

source /opt/gugik2osm/venv/bin/activate

date >> /opt/gugik2osm/log/bdot_processing.log
echo "Downloading bdot10k files..." >> /opt/gugik2osm/log/bdot_processing.log
python3 -u /opt/gugik2osm/git/processing/scripts/bdot_dl.py --output_dir /opt/gugik2osm/tempbdot --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/bdot_processing.log 2>&1
date >> /opt/gugik2osm/log/bdot_processing.log
