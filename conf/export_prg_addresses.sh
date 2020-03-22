psql -d gugik2osm -f /opt/gugik2osm/git/processing/sql/export/prg_addresses.sql | zip -9 /opt/gugik2osm/temp/export/prg_addresses.zip -
cp /opt/gugik2osm/temp/export/prg_addresses.zip /var/www/data/prg_addresses.zip
