#!/bin/bash 

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

date >> /opt/gugik2osm/log/teryt_processing.log
python3 -u /opt/gugik2osm/git/processing/scripts/teryt_dl.py --api_env prod --dotenv /opt/gugik2osm/conf/.env >> /opt/gugik2osm/log/teryt_processing.log 2>&1
date >> /opt/gugik2osm/log/teryt_processing.log
