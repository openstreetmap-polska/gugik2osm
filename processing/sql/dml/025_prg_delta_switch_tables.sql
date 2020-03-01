alter table prg.delta rename to delta_old;
alter table prg.delta_new rename to delta;
drop table prg.delta_old;
