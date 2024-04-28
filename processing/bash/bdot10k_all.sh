#!/usr/bin/env bash

# exit on error in any command
set -e

/opt/gugik2osm/git/processing/bdot10k_dl.sh
/opt/gugik2osm/git/processing/bdot10k_bubd_a_parse.sh
/opt/gugik2osm/git/processing/bdot10k_bubd_a_export.sh
