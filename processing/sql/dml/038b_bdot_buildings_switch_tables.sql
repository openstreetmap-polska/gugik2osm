drop table if exists bdot_buildings_old;
alter table bdot_buildings rename to bdot_buildings_old;
alter index idx_bdot_buildings_geom rename to idx_bdot_buildings_geom_old;
alter table bdot_buildings_new rename to bdot_buildings;
alter index idx_bdot_buildings_geom_new rename to idx_bdot_buildings_geom;

drop table if exists bdot_buildings_all_old;
alter table bdot_buildings_all rename to bdot_buildings_all_old;
alter index idx_bdot_buildings_all_geom rename to idx_bdot_buildings_all_geom_old;
alter table bdot_buildings_all_new rename to bdot_buildings_all;
alter index idx_bdot_buildings_all_geom_new rename to idx_bdot_buildings_all_geom;
