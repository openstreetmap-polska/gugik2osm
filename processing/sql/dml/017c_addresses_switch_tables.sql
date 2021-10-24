drop table if exists addresses_old;
alter table if exists addresses rename to addresses_old;
alter table addresses_new rename to addresses;

alter index addresses_geom rename to addresses_old_geom;
alter index addresses_lokalnyid rename to addresses_old_lokalnyid;
alter index addresses_new_geom rename to addresses_geom;
alter index addresses_new_lokalnyid rename to addresses_lokalnyid;
