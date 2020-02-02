create index osm_hashed_geom on osm_hashed using gist (geom);
cluster osm_hashed USING osm_hashed_geom;
