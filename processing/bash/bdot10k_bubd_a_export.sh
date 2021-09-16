#!/bin/bash

# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=1000 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip /var/www/data/bdot10k_bubd_a.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '02%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.zip /var/www/data/bdot10k_bubd_a_dolnoslaskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '04%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.zip /var/www/data/bdot10k_bubd_a_kujawsko_pomorskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '06%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.zip /var/www/data/bdot10k_bubd_a_lubelskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '08%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.zip /var/www/data/bdot10k_bubd_a_lubuskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '10%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.zip /var/www/data/bdot10k_bubd_a_lodzkie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '12%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.zip /var/www/data/bdot10k_bubd_a_malopolskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '14%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.zip /var/www/data/bdot10k_bubd_a_mazowieckie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '16%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.zip /var/www/data/bdot10k_bubd_a_opolskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '18%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.zip /var/www/data/bdot10k_bubd_a_podkarpackie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '20%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.zip /var/www/data/bdot10k_bubd_a_podlaskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '22%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.zip /var/www/data/bdot10k_bubd_a_pomorskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '24%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.zip /var/www/data/bdot10k_bubd_a_slaskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '26%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.zip /var/www/data/bdot10k_bubd_a_swietokrzyskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '28%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.zip /var/www/data/bdot10k_bubd_a_warminsko_mazurskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '30%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.zip /var/www/data/bdot10k_bubd_a_wielkopolskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '32%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg
mv /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.zip /var/www/data/bdot10k_bubd_a_zachodniopomorskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg


date >> /opt/gugik2osm/log/bdot_processing.log