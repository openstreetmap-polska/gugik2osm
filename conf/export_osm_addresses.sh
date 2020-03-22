psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/osm_addresses.sql > /opt/gugik2osm/temp/export/osm_addresses.csv
zip -9 /opt/gugik2osm/temp/export/osm_addresses.zip /opt/gugik2osm/temp/export/osm_addresses.csv
mv /opt/gugik2osm/temp/export/osm_addresses.zip /var/www/data/osm_addresses.zip
