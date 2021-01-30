drop table if exists bdot_buildings_old;
alter table bdot_buildings rename to bdot_buildings_old;
alter index idx_bdot_buildings_geom rename to idx_bdot_buildings_geom_old;
alter table bdot_buildings_new rename to bdot_buildings;
alter index idx_bdot_buildings_geom_new rename to idx_bdot_buildings_geom;
