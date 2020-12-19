create table if not exists osm_stats (
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
  measurement_day date not null,
  metric_key text not null,
  metric_description text not null,
  value int not null,
  constraint osm_stats_pk primary key (measurement_day, metric_key)
);

set work_mem = '512MB';

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_addr_point_count',
  'Liczba adresów przypisanych do punktu.',
  (select count(*) from osm_addr_point)
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_addr_polygon_count',
  'Liczba adresów przypisanych do poligonu.',
  (select count(*) from osm_addr_polygon)
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_addr_point_and_polygon_count',
  'Całkowita liczba adresów.',
  (select count(*) from osm_addr_point)
  +
  (select count(*) from osm_addr_polygon)
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_addr_postcode_count',
  'Liczba adresów z kodem pocztowym',
  (select count(*) from osm_addr_point where kod_pna is not null and kod_pna <> '')
  +
  (select count(*) from osm_addr_polygon where kod_pna is not null and kod_pna <> '')
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_unique_addresses_count',
  'Liczba unikalnych adresów.',
  (select count(*) from (
    select distinct md5(concat(coalesce(miejscowosc, cz_msc, ''), coalesce(ulica, ''), type)) adr_hash
    from osm_addr_point
    union
    select distinct md5(concat(coalesce(miejscowosc, cz_msc, ''), coalesce(ulica, ''), type)) adr_hash
    from osm_addr_polygon
  ) adr )
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_unique_addresses_postcode_count',
  'Liczba unikalnych adresów z kodami pocztowymi.',
  (select count(*) from (
    select distinct md5(concat(coalesce(miejscowosc, cz_msc, ''), coalesce(ulica, ''), type)) adr_hash
    from osm_addr_point
    where kod_pna is not null and kod_pna <> ''
    union
    select distinct md5(concat(coalesce(miejscowosc, cz_msc, ''), coalesce(ulica, ''), type)) adr_hash
    from osm_addr_polygon
    where kod_pna is not null and kod_pna <> ''
  ) adr )
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_buildings_count',
  'Liczba budynków.',
  (select count(*) from osm_buildings)
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_buidlings_tag_flats_count',
  'Liczba budynków z tagiem building:flats.',
  (select count(*) from osm_buildings where liczba_mieszkan is not null and liczba_mieszkan <> '')
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_buidlings_tag_levels_count',
  'Liczba budynków z tagiem building:levels.',
  (select count(*) from osm_buildings where kondygnacje is not null and kondygnacje <> '')
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_buidlings_tag_height_count',
  'Liczba budynków z tagiem building:height.',
  (select count(*) from osm_buildings where wysokosc_npg is not null and wysokosc_npg <> '')
);

insert into osm_stats (measurement_day, metric_key, metric_description, value) values (
  CURRENT_DATE,
  'osm_buidlings_tag_roofshape_count',
  'Liczba budynków z tagiem roof:shape.',
  (select count(*) from osm_buildings where ksztalt_dachu is not null and ksztalt_dachu <> '')
);

insert into osm_stats (measurement_day, metric_key, metric_description, value)
  select
    CURRENT_DATE,
    'osm_buidlings_tag_building:' || budynek || '_count',
    'Liczba budynków z tagiem X dla budynku, gdzie X to jeden z 10 najpopularniejszych tagów.',
    cnt
  from (
    select budynek, count(*) cnt from osm_buildings group by 1 order by 2 desc limit 10
  ) t
;
