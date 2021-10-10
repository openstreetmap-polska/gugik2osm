select st_asgeojson(geometry) from osm_admin where osm_id = (-1 * %(relation_id)s);
