psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/teryt_ul.sql > /opt/gugik2osm/temp/export/teryt_ul.csv
mv /opt/gugik2osm/temp/export/teryt_ul.csv /var/www/data/teryt_ul.csv
