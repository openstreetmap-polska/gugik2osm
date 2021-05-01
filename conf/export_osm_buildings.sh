#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/osm_buildings.gpkg PG:"dbname=gugik2osm" "osm_buildings" -nln "budynki" -gt 65536 -select "osm_id,budynek,kondygnacje,ksztalt_dachu,liczba_mieszkan,kondygnacje_podziemne,wysokosc_npg,geometry" -overwrite
zip -9 -j /opt/gugik2osm/temp/export/osm_buildings.zip /opt/gugik2osm/temp/export/osm_buildings.gpkg
rm /opt/gugik2osm/temp/export/osm_buildings.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/osm_buildings.zip osm_buildings.zip
rm /opt/gugik2osm/temp/export/osm_buildings.zip
