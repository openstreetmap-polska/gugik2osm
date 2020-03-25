psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_gmi.sql > /opt/gugik2osm/temp/export/teryt_gmi.csv
mv /opt/gugik2osm/temp/export/teryt_gmi.csv /var/www/data/teryt_gmi.csv
