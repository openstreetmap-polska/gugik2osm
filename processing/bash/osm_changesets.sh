#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

python3 -u /opt/gugik2osm/git/processing/scripts/osm_changesets_dl.py --changesets-dir /opt/gugik2osm/temp_changesets/ --auto-starting-point >> /opt/gugik2osm/log/osm_changesets.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/osm_changesets.py --changesets-dir /opt/gugik2osm/temp_changesets/ --dotenv /opt/gugik2osm/conf/.env --restrict-to-bbox poland --process-not-loaded-yet >> /opt/gugik2osm/log/osm_changesets.log 2>&1
