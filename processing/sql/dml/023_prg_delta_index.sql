create index if not exists delta_gis on prg.delta using gist (geom);
cluster prg.delta using delta_gis;
create index if not exists delta_lokalnyid on prg.delta using btree (lokalnyid);
alter table prg.delta set logged;
