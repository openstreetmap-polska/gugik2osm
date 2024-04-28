#!/usr/bin/env bash

# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

source /opt/gugik2osm/venv/bin/activate

python3 -u /opt/gugik2osm/git/processing/scripts/prg_dl.py --output_dir /opt/gugik2osm/tempprg >> /opt/gugik2osm/log/prg_processing.log 2>&1
date >> /opt/gugik2osm/log/prg_processing.log
echo "PRG2CSV" >> /opt/gugik2osm/log/prg_processing.log
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/02_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/04_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/06_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/08_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/10_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/12_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/14_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/16_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/18_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/20_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/22_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/24_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/26_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/28_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/30_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/tempprg/32_Punkty_Adresowe.zip --writer csv --csv_directory /opt/gugik2osm/tempprg2 >> /opt/gugik2osm/log/prg_processing.log 2>&1
date >> /opt/gugik2osm/log/prg_processing.log
echo "CSV2PGSQL" >> /opt/gugik2osm/log/prg_processing.log
echo "truncate" >> /opt/gugik2osm/log/prg_processing.log
psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "truncate table prg.jednostki_administracyjne" >> /opt/gugik2osm/log/prg_processing.log 2>&1
psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "truncate table prg.miejscowosci" >> /opt/gugik2osm/log/prg_processing.log 2>&1
psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "truncate table prg.ulice" >> /opt/gugik2osm/log/prg_processing.log 2>&1
psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "truncate table prg.punkty_adresowe" >> /opt/gugik2osm/log/prg_processing.log 2>&1
echo "load" >> /opt/gugik2osm/log/prg_processing.log
for infile in /opt/gugik2osm/tempprg2/*JednostkaAdministracyjna*.csv
do
  cat $infile | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy prg.jednostki_administracyjne FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1
done
for infile in /opt/gugik2osm/tempprg2/*PRG_MiejscowoscNazwa*.csv
do
  cat $infile | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy prg.miejscowosci FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1
done
for infile in /opt/gugik2osm/tempprg2/*PRG_UlicaNazwa*.csv
do
  cat $infile | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy prg.ulice FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1
done
for infile in /opt/gugik2osm/tempprg2/*PRG_PunktAdresowy*.csv
do
  cat $infile | psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "copy prg.punkty_adresowe FROM stdin with CSV header delimiter ','" >> /opt/gugik2osm/log/prg_processing.log 2>&1
done
python3 -u /opt/gugik2osm/git/processing/scripts/prg_prepare.py --full --dotenv /opt/gugik2osm/conf/.env --starting 001_prg_pa_insert.sql >> /opt/gugik2osm/log/prg_processing.log 2>&1
echo "Finished preparing data" >> /opt/gugik2osm/log/prg_processing.log
date >> /opt/gugik2osm/log/prg_processing.log
echo "Exporting unmatched streets" >> /opt/gugik2osm/log/prg_processing.log
psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -f /opt/gugik2osm/git/processing/sql/export/osm_street_mapping.sql > /opt/gugik2osm/temp/export/unmatched_osm_street_mappings.csv
mv /opt/gugik2osm/temp/export/unmatched_osm_street_mappings.csv /var/www/data/unmatched_osm_street_mappings.csv
date >> /opt/gugik2osm/log/prg_processing.log
echo "Cleaning temp csv files..." >> /opt/gugik2osm/log/prg_processing.log
rm /opt/gugik2osm/tempprg2/*.csv
date >> /opt/gugik2osm/log/prg_processing.log
echo "Cleaning temp zip files..." >> /opt/gugik2osm/log/prg_processing.log
rm /opt/gugik2osm/tempprg/*.zip
echo "Done." >> /opt/gugik2osm/log/prg_processing.log
date >> /opt/gugik2osm/log/prg_processing.log
