ogr2ogr -f "GPKG" /opt/gugik2osm/temp/export/osm_buildings.gpkg PG:"dbname='gugik2osm" "osm_buildings" -nln "budynki" -gt 65536 -overwrite
zip -9 -j /opt/gugik2osm/temp/export/osm_buildings.zip /opt/gugik2osm/temp/export/osm_buildings.gpkg
mv /opt/gugik2osm/temp/export/osm_buildings.zip /var/www/data/osm_buildings.zip
rm /opt/gugik2osm/temp/export/osm_buildings.gpkg
