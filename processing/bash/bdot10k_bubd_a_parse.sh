#!/bin/bash

# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

source /opt/gugik2osm/venv/bin/activate

date >> /opt/gugik2osm/log/bdot_processing.log
echo "BDOT2CSV" >> /opt/gugik2osm/log/bdot_processing.log
python3 -u /opt/gugik2osm/git/processing/parsers/bdot10k.py --input /opt/gugik2osm/tempbdot/BDOT10k_*.zip --writer csv --csv_directory /opt/gugik2osm/tempbdot2/ --basic_fields >> /opt/gugik2osm/log/bdot_processing.log 2>&1
date >> /opt/gugik2osm/log/bdot_processing.log
echo "CSV2PGSQL" >> /opt/gugik2osm/log/bdot_processing.log
psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "truncate table bdot.stg_budynki_ogolne_poligony" >> /opt/gugik2osm/log/bdot_processing.log 2>&1
for infile in /opt/gugik2osm/tempbdot2/*.csv
do
  cat $infile | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy bdot.stg_budynki_ogolne_poligony FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/bdot_processing.log 2>&1
done
date >> /opt/gugik2osm/log/bdot_processing.log
echo "Cleaning temp csv files..." >> /opt/gugik2osm/log/bdot_processing.log
rm /opt/gugik2osm/tempbdot2/*.csv
date >> /opt/gugik2osm/log/bdot_processing.log
echo "Cleaning temp zip files..." >> /opt/gugik2osm/log/bdot_processing.log
rm /opt/gugik2osm/tempbdot/*.zip
date >> /opt/gugik2osm/log/bdot_processing.log
