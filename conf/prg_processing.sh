#!/bin/bash

source /opt/gugik2osm/conf/.env

python3 -u /opt/gugik2osm/git/processing/scripts/prg_dl.py --output_dir /opt/gugik2osm/temp >> /opt/gugik2osm/log/prg_processing.log 2>&1
date >> /opt/gugik2osm/log/prg_processing.log
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/02_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" --prep_tables >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/04_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/06_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/08_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/10_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/12_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/14_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/16_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/18_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/20_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/22_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/24_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/26_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/28_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/30_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
python3 -u /opt/gugik2osm/git/processing/parsers/prg.py --input /opt/gugik2osm/temp/32_Punkty_Adresowe.zip --writer postgresql --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" >> /opt/gugik2osm/log/prg_processing.log 2>&1
date >> /opt/gugik2osm/log/prg_processing.log
python3 -u /opt/gugik2osm/git/processing/scripts/prg_prepare.py --full --dsn "host=$PGHOSTADDR port=$PGPORT dbname=$PGDATABASE user=$PGUSER password=$PGPASSWORD" --starting 001_prg_pa_insert.sql >> /opt/gugik2osm/log/prg_processing.log 2>&1
echo "Finished preparing data" >> /opt/gugik2osm/log/prg_processing.log
date >> /opt/gugik2osm/log/prg_processing.log
bash /opt/gugik2osm/conf/cache_low_zoom_tiles.sh
echo "Finished caching low zoom tiles" >> /opt/gugik2osm/log/prg_processing.log
date >> /opt/gugik2osm/log/prg_processing.log
