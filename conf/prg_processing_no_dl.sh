#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

date >> /opt/gugik2osm/log/prg_processing.log
python3 -u /opt/gugik2osm/git/processing/scripts/prg_prepare.py --full --dotenv /opt/gugik2osm/conf/.env --starting 001_prg_pa_insert.sql >> /opt/gugik2osm/log/prg_processing.log 2>&1
date >> /opt/gugik2osm/log/prg_processing.log
