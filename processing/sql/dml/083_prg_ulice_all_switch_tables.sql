drop table if exists streets_all_old;
alter table streets_all rename to streets_all_old;
alter table streets_all_new rename to streets_all;
