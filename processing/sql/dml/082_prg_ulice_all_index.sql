create index on streets_all_new using gist (geom_2180);
alter table streets_all_new add primary key (street_id);
