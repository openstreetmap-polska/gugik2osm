drop table if exists streets_all_new;
create table streets_all_new (
  street_id uuid not null,
  interpolated_teryt_simc text,
  teryt_ulic text,
  street_name text,
  geom_2180 geometry not null
);
