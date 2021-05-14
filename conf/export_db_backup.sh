#!/bin/bash

# exit on error in any command
set -e

source /opt/gugik2osm/venv/bin/activate

pg_dump --format c --compress 9 --no-owner --no-privileges --file /opt/gugik2osm/temp/export/db.bak --dbname gugik2osm
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/db.bak dbbackup/db.bak
rm /opt/gugik2osm/temp/export/db.bak

pg_dump --format p --schema-only --no-owner --no-privileges --file /opt/gugik2osm/temp/export/db_only_schema.sql --dbname gugik2osm
b2 upload-file gugik2osm /opt/gugik2osm/temp/export/db_only_schema.sql dbbackup/db_only_schema.sql
rm /opt/gugik2osm/temp/export/db_only_schema.sql
