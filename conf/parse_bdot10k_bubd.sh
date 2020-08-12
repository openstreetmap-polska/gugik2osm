#!/bin/bash

source /opt/gugik2osm/conf/.env

date >> /opt/gugik2osm/log/bdot_processing.log
echo "Processing BDOT files..." >> /opt/gugik2osm/log/bdot_processing.log
python3.7 -u /opt/gugik2osm/git/processing/parsers/bdot10k.py --input /opt/gugik2osm/tempbdot/BDOT10k_*.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" --prep_tables --basic_fields --create_lookup_tables --create_view >> /opt/gugik2osm/log/bdot_processing.log 2>&1
date >> /opt/gugik2osm/log/bdot_processing.log

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" "bdot.v_bubd_a" -nln "bubd_a" -gt 65536 -overwrite >> /opt/gugik2osm/log/bdot_processing.log 2>&1
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip /var/www/data/bdot10k_bubd_a.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg

date >> /opt/gugik2osm/log/bdot_processing.log
