#!/usr/bin/env bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

python3 -u /opt/gugik2osm/git/processing/scripts/expired_tiles.py --insert-exp-tiles --dir /opt/gugik2osm/imposm3/exptiles/ --dotenv /opt/gugik2osm/conf/.env >> /opt/gugik2osm/log/data_update.log 2>&1
python3 -u /opt/gugik2osm/git/processing/scripts/prg_prepare.py --update --dotenv /opt/gugik2osm/conf/.env >> /opt/gugik2osm/log/data_update.log 2>&1
