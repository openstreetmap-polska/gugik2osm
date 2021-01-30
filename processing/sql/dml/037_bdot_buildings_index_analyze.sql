create index if not exists idx_bdot_buildings_geom_new on bdot_buildings_new using GIST (geom_4326);
analyze bdot_buildings_new;
