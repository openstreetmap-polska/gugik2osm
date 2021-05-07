#!/bin/bash

source /opt/gugik2osm/conf/.env

source /opt/gugik2osm/venv/bin/activate

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=1000 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip bdot10k_bubd_a.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '02%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.zip bdot10k_bubd_a_dolnoslaskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_dolnoslaskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '04%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.zip bdot10k_bubd_a_kujawsko_pomorskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_kujawsko_pomorskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '06%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.zip bdot10k_bubd_a_lubelskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubelskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '08%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.zip bdot10k_bubd_a_lubuskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lubuskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '10%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.zip bdot10k_bubd_a_lodzkie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_lodzkie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '12%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.zip bdot10k_bubd_a_malopolskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_malopolskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '14%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.zip bdot10k_bubd_a_mazowieckie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_mazowieckie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '16%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.zip bdot10k_bubd_a_opolskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_opolskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '18%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.zip bdot10k_bubd_a_podkarpackie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podkarpackie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '20%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.zip bdot10k_bubd_a_podlaskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_podlaskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '22%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.zip bdot10k_bubd_a_pomorskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_pomorskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '24%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.zip bdot10k_bubd_a_slaskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_slaskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '26%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.zip bdot10k_bubd_a_swietokrzyskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_swietokrzyskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '28%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.zip bdot10k_bubd_a_warminsko_mazurskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_warminsko_mazurskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '30%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.zip bdot10k_bubd_a_wielkopolskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_wielkopolskie.zip

echo "Creating GeoPackage..." >> /opt/gugik2osm/log/bdot_processing.log

ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg PG:"dbname='$PGDATABASE' host='$PGHOSTADDR' port='$PGPORT' user='$PGUSER' password='$PGPASSWORD'" -sql "select * from bdot.v_bubd_a where powiat like '32%'" -nln "bubd_a" -gt 65536 -overwrite --config OGR_SQLITE_CACHE=500 --config OGR_SQLITE_SYNCHRONOUS=OFF >> /opt/gugik2osm/log/bdot_processing.log 2>&1
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg -sql "VACUUM"
ogrinfo /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg -sql "ANALYZE"
zip -9 -j /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.zip /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.gpkg
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.zip bdot10k_bubd_a_zachodniopomorskie.zip
rm /opt/gugik2osm/temp/export/bdot10k_bubd_a_zachodniopomorskie.zip


date >> /opt/gugik2osm/log/bdot_processing.log