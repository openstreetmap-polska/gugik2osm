psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/osm_addresses.sql | zip -9 /opt/gugik2osm/temp/export/osm_addresses.zip -
cp /opt/gugik2osm/temp/export/osm_addresses.zip /var/www/data/osm_addresses.zip
