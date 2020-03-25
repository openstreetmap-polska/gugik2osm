psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_pow.sql > /opt/gugik2osm/temp/export/teryt_pow.csv
mv /opt/gugik2osm/temp/export/teryt_pow.csv /var/www/data/teryt_pow.csv
