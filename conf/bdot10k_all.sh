#!/bin/bash

# exit on error in any command
set -e

/opt/gugik2osm/conf/bdot10k_dl.sh
/opt/gugik2osm/conf/bdot10k_bubd_a_parse.sh
/opt/gugik2osm/conf/bdot10k_bubd_a_export.sh
