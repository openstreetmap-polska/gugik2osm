select st_asgeojson(geometry) from osm_admin where tags -> 'teryt:terc' = %(terc_code)s;
