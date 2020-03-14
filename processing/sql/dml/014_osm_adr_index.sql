create index osm_adr_geom on osm_adr using gist (geom);
analyze osm_adr;
