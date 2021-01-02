alter table prg.delta rename to delta_old;
alter table prg.delta_new rename to delta;
alter index prg.delta_gis rename to delta_gis_old;
alter index prg.delta_lokalnyid rename to delta_lokalnyid_old;
alter index prg.delta_simc rename to delta_simc_old;
alter index prg.delta_gis_new rename to delta_gis;
alter index prg.delta_lokalnyid_new rename to delta_lokalnyid;
alter index prg.delta_simc_new rename to delta_simc;
