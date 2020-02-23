create index osm_hashed_geom on osm_hashed using gist (geom);
cluster osm_hashed USING osm_hashed_geom;
create index osm_hashed_md5 on osm_hashed using btree (hash);
alter table osm_hashed set logged;
