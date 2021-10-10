select st_asgeojson(geometry) from osm_admin where tags -> 'teryt:simc' = %(simc_code)s;
