create table if not exists street_names_mappings (
  teryt_simc_code text not null,
  teryt_ulic_code text not null,
  teryt_street_name text not null,
  osm_street_name text not null,
  constraint street_names_mappings_pk primary key (teryt_simc_code, teryt_ulic_code)
);
