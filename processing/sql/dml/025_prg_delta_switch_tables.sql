alter table prg.delta rename to delta_old;
alter table prg.delta_new rename to delta;
drop table prg.delta_old;
alter index prg.delta_gis_new rename to delta_gis;
alter index prg.delta_lokalnyid_new rename to delta_lokalnyid;
vacuum analyze prg.delta;
