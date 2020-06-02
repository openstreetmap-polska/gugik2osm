pg_dump --format c --compress 9 --no-owner --no-privileges --file /opt/gugik2osm/temp/export/db.bak --dbname gugik2osm
mv /opt/gugik2osm/temp/export/db.bak /var/www/data/dbbackup/db.bak

pg_dump --format p --schema-only --no-owner --no-privileges --file /opt/gugik2osm/temp/export/db_only_schema.sql --dbname gugik2osm
mv /opt/gugik2osm/temp/export/db_only_schema.sql /var/www/data/dbbackup/db_only_schema.sql
