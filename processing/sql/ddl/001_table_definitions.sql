-- schemas
CREATE SCHEMA IF NOT EXISTS bdot;
CREATE SCHEMA IF NOT EXISTS changesets_processing;
CREATE SCHEMA IF NOT EXISTS prg;
CREATE SCHEMA IF NOT EXISTS teryt;

-- extensions
CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;

-- tables
-- -------------------------------------------------------------
-- bdot

create table if not exists bdot.buildings_categories_mappings (
  kategoria_bdot text not null,
  funkcja_ogolna_budynku text not null,
  funkcja_szczegolowa_budynku text not null,
  building text,
  amenity text,
  man_made text,
  leisure text,
  historic text,
  tourism text,
  constraint buildings_categories_mappings_pk primary key (kategoria_bdot, funkcja_ogolna_budynku, funkcja_szczegolowa_budynku)
);

create table if not exists bdot_buildings (
    powiat text not null,
    lokalnyid uuid primary key,
    status_bdot text not null,
    -- dane bdot
    kategoria_bdot text,
    funkcja_ogolna_budynku text,
    funkcja_szczegolowa_budynku text,
    aktualnosc_geometrii date,
    aktualnosc_atrybutow date,
    -- zmapowane tagi osm
    building text,
    amenity text,
    man_made text,
    leisure text,
    historic text,
    tourism text,
    building_levels smallint,
    geom_4326 geometry(geometry, 4326) not null
);
CREATE INDEX if not exists idx_bdot_buildings_geom ON bdot_buildings USING gist (geom_4326);

CREATE TABLE IF NOT EXISTS bdot_buildings_all (
    powiat text NOT NULL,
    lokalnyid uuid primary key,
    status_bdot text NOT NULL,
    kategoria_bdot text,
    funkcja_ogolna_budynku text,
    funkcja_szczegolowa_budynku text,
    aktualnosc_geometrii date,
    aktualnosc_atrybutow date,
    building text,
    amenity text,
    man_made text,
    leisure text,
    historic text,
    tourism text,
    building_levels smallint,
    geom_4326 geometry(geometry, 4326) NOT NULL
);
create index if not exists idx_bdot_buildings_all_geom on bdot_buildings_all using GIST (geom_4326);

create unlogged table if not exists bdot.stg_budynki_ogolne_poligony (
    lokalnyid              text,
    wersjaid               text,
    x_kod                  text,
    x_skrkarto             text,
    x_katistnienia         text,
    x_aktualnoscg          text,
    x_aktualnosca          text,
    koniecwersjiobiektu    text,
    funogolnabudynku       text,
    funszczegolowabudynku  text,
    funszczegolowabudynku_01  text,
    funszczegolowabudynku_02  text,
    funszczegolowabudynku_03  text,
    funszczegolowabudynku_04  text,
    funszczegolowabudynku_05  text,
    funszczegolowabudynku_06  text,
    funszczegolowabudynku_07  text,
    funszczegolowabudynku_08  text,
    funszczegolowabudynku_09  text,
    funszczegolowabudynku_10  text,
    liczbakondygnacji      text,
    kodkst                 text,
    nazwa                  text,
    zabytek                text,
    geometry               text,
    powiat                 text
);

create table if not exists bdot.lookup_funogolnabudynku (
   funogolnabudynku        text primary key,
   funkcja_ogolna_budynku  text not null
);

create table if not exists bdot.lookup_funszczegolowabudynku (
   funszczegolowabudynku        text primary key,
   funkcja_szczegolowa_budynku  text not null
);

create table if not exists bdot.lookup_x_katistnienia (
   x_katistnienia          text primary key,
   status_bdot             text not null
);

create table if not exists bdot.lookup_x_kod (
   x_kod                   text primary key,
   kategoria_bdot          text not null
);

-- -------------------------------------------------------------
-- changesets_processing

CREATE TABLE IF NOT EXISTS changesets_processing.processed_files (
    file_path text not null primary key,
    inserted_at timestamp with time zone not null default CURRENT_TIMESTAMP
);
create index if not exists idx_processed_files_ts_inserted on changesets_processing.processed_files (inserted_at);

CREATE TABLE IF NOT EXISTS changesets_processing.changesets (
    file_path text not null,
    changeset_id integer not null,
    created_at timestamp with time zone not null,
    closed_at timestamp with time zone,
    open boolean,
    num_changes integer,
    osm_user text not null,
    uid integer not null,
    comments_count integer,
    tags jsonb,
    bbox geometry(Polygon, 4326),
    primary key (file_path, changeset_id),
    foreign key (file_path) REFERENCES changesets_processing.processed_files ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);
-- create index if not exists idx_changesets_ts on changesets_processing.changesets using brin (created_at) with (pages_per_range=64, autosummarize = on);
create index if not exists idx_changesets_ts_created on changesets_processing.changesets (created_at);
create index if not exists idx_changesets_ts_closed on changesets_processing.changesets (closed_at);
create index if not exists idx_changesets_geom on changesets_processing.changesets using gist (bbox);

-- -------------------------------------------------------------
-- prg
CREATE TABLE IF NOT EXISTS prg.delta (
    lokalnyid uuid primary key,
    teryt_msc text,
    teryt_simc text,
    teryt_ulica text,
    teryt_ulic text,
    nr text,
    pna text,
    geom geometry,
    nr_standaryzowany text
);
CREATE INDEX if not exists delta_gis ON prg.delta USING gist (geom);
create index if not exists delta_lokalnyid on prg.delta using btree (lokalnyid);
create index if not exists delta_simc on prg.delta using hash (teryt_simc);

CREATE TABLE IF NOT EXISTS prg.pa (
    lokalnyid uuid primary key,
    woj text,
    pow text,
    gmi text,
    terc6 text,
    teryt7 text,
    msc text NOT NULL,
    simc text,
    ul text,
    ulic text,
    numerporzadkowy text NOT NULL,
    nr text NOT NULL,
    pna text,
    gml geometry,
    teryt_msc text,
    teryt_simc text,
    teryt_ulica text,
    teryt_ulic text,
    osm_ulica text
);
--CREATE INDEX if not exists prg_pa_geom ON prg.pa USING gist (geometry);

CREATE TABLE IF NOT EXISTS prg.pa_hashed (
    hash text,
    lokalnyid uuid,
    geom geometry
);
CREATE INDEX if not exists prg_pa_hashed_geom ON prg.pa_hashed USING gist (geom);

CREATE TABLE IF NOT EXISTS addresses (
    lokalnyid uuid,
    teryt_msc text,
    teryt_simc text,
    teryt_ulica text,
    teryt_ulic text,
    nr text,
    pna text,
    nr_standaryzowany text,
    geom_2180 geometry
);
create index if not exists addresses_lokalnyid on addresses using btree (lokalnyid);
CREATE INDEX if not exists addresses_geom ON addresses USING gist (geom_2180);

CREATE UNLOGGED TABLE IF NOT EXISTS prg.jednostki_administracyjne (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    nazwa text,
    idteryt text,
    poziom text,
    jednostkapodzialuteryt text
);
CREATE UNLOGGED TABLE IF NOT EXISTS prg.miejscowosci (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    nazwa text,
    idteryt text,
    geometry text,
    miejscowosc text
);
CREATE UNLOGGED TABLE IF NOT EXISTS prg.ulice (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    nazwaglownaczesc text,
    idteryt text,
    geometry text,
    ulica text
);
CREATE UNLOGGED TABLE IF NOT EXISTS prg.punkty_adresowe (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    jednostkaadministracyjna text,
    jednostkaadministracyjna_01 text,
    jednostkaadministracyjna_02 text,
    jednostkaadministracyjna_03 text,
    miejscowosc text,
    czescmiejscowosci text,
    ulica text,
    numerporzadkowy text,
    kodpocztowy text,
    status text,
    geometry text,
    komponent text,
    komponent_01 text,
    komponent_02 text,
    komponent_03 text,
    komponent_04 text,
    komponent_05 text,
    komponent_06 text,
    obiektemuia text
);

-- -------------------------------------------------------------
-- app/update process general
create table if not exists exclude_prg (
  id uuid primary key,
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP
);
create index if not exists idx_exclude_prg_created_ts on exclude_prg(created_at);

create table if not exists exclude_prg_queue (
  id uuid primary key,
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
  processed bool not null default false
);

create table if not exists exclude_bdot_buildings (
  id uuid primary key,
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP
);
create index if not exists idx_exclude_bdot_buildings_created_ts on exclude_bdot_buildings(created_at);

create table if not exists exclude_bdot_buildings_queue (
  id uuid primary key,
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
  processed bool not null default false
);

create table if not exists expired_tiles (
    file_name text not null,
    z int not null,
    x int not null,
    y int not null,
    processed bool not null default false,
    created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
    constraint expired_tiles_pk primary key (file_name, z, x, y)
);
create index if not exists idx_expired_tiles_created_ts on expired_tiles(created_at);
create index if not exists idx_expired_tiles_not_processed on expired_tiles(processed) where not processed;

create table if not exists package_exports (
  export_id bigint generated by default as identity,
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
  bbox geometry(geometry, 3857) not null,
  adresy int,
  budynki int
);
create index if not exists idx_package_exports_created_at on package_exports(created_at);

create table if not exists tiles (
    z integer not null,
    x integer not null,
    y integer not null,
    mvt bytea,
    bbox geometry(Polygon, 3857),
    constraint tiles_zxy_pk primary key (z, x, y)
);
create index if not exists idx_tiles_bbox on tiles using gist (bbox);

create table if not exists tiles_bounds (
    z int,
    x int,
    y int,
    geom_3857 geometry(Polygon, 3857),
    primary key (z, x, y)
);
create index if not exists idx_tiles_bounds_geom on tiles_bounds using gist (geom_3857);

CREATE TABLE if not exists prng (
    id integer,
    geom geometry(Point,4326),
    liczba_adresow bigint,
    liczba_budynkow bigint,
    count bigint
);
CREATE INDEX if not exists idx_prng_count ON prng USING btree (count DESC);
CREATE INDEX if not exists idx_prng_geom ON prng USING gist (geom);

CREATE TABLE if not exists process_locks (
    process_name text primary key,
    in_progress boolean NOT NULL,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    last_status text,
    pretty_name text
);

CREATE TABLE if not exists stg_prng_miejscowosci (
    id integer NOT NULL,
    geom geometry(Point,4326),
    "identyfikator prng" integer,
    "nazwa główna" character varying,
    "rodzaj obiektu" character varying,
    "klasa obiektu" character varying,
    "obiekt nadrzędny" character varying,
    "funkcja administracyjna miejscowości" character varying,
    "dopełniacz" character varying,
    przymiotnik character varying,
    uwagi character varying,
    "źródło informacji" character varying,
    "element rozróżniający" character varying,
    "element rodzajowy" character varying,
    "wymowa ipa" character varying,
    "wymowa polska" character varying,
    "szerokość geograficzna" character varying,
    "długość geograficzna" character varying,
    "współrzędne prostokątne y" character varying,
    "współrzędne prostokątne x" character varying,
    "data modyfikacji" character varying,
    "rodzaj reprezentacji" character varying,
    "system zewnętrzny" character varying,
    "identyfikator zewnętrzny" integer,
    "identyfikator iip" character varying,
    "skala mapy" character varying,
    "status nazwy" character varying,
    "nazwa dodatkowa" character varying,
    "kod języka nazwy dodatkowej" character varying,
    "język nazwy dodatkowej" character varying,
    "latynizacja nazwy dodatkowej" character varying,
    "nazwa historyczna" character varying,
    "nazwa oboczna" character varying,
    "uwagi nazw dodatkowych" character varying,
    "uwagi nazw historycznych" character varying,
    "uwagi nazw obocznych" character varying,
    "obcy egzonim" character varying,
    "pismo egzonimu" character varying,
    "język egzonimu" character varying,
    "latynizacja egzonimu" character varying,
    "zagraniczny endonim" character varying,
    "pismo endonimu" character varying,
    "język endonimu" character varying,
    "latynizacja endonimu" character varying,
    "państwo" character varying,
    "województwo" character varying,
    powiat character varying,
    gmina character varying,
    "identyfikator jednostki podziału terytorialnego kraju" integer,
    "data wprowadzenia" character varying,
    "data zniesienia lub usunięcia" character varying,
    "przestrzeń nazw" character varying
);

CREATE TABLE if not exists streets_all (
    street_id uuid primary key,
    interpolated_teryt_simc text,
    teryt_ulic text,
    street_name text,
    geom_2180 geometry NOT NULL
);
CREATE INDEX if not exists streets_all_new_geom_2180_idx1 ON streets_all USING gist (geom_2180);

-- -------------------------------------------------------------
-- teryt
create table if not exists street_names_mappings (
  teryt_simc_code text not null,
  teryt_ulic_code text not null,
  teryt_street_name text not null,
  osm_street_name text not null,
  constraint street_names_mappings_pk primary key (teryt_simc_code, teryt_ulic_code)
);

create table if not exists teryt.cecha_mapping (
    cecha text primary key,
    m text not null
);
CREATE TABLE if not exists teryt.simc (
    woj text,
    pow text,
    gmi text,
    rodz_gmi text,
    rm text,
    mz text,
    nazwa text,
    sym text,
    sympod text,
    stan_na text
);
CREATE TABLE if not exists teryt.terc (
    woj text,
    pow text,
    gmi text,
    rodz text,
    nazwa text,
    nazdod text,
    stan_na text
);
CREATE TABLE if not exists teryt.ulic (
    woj text,
    pow text,
    gmi text,
    rodz_gmi text,
    sym text,
    sym_ul text,
    cecha text,
    nazwa_1 text,
    nazwa_2 text,
    stan_na text
);
CREATE TABLE if not exists teryt.wmrodz (
    rm text,
    nazwa_rm text,
    stan_na text
);

-- -------------------------------------------------------------
-- osm

CREATE TABLE IF NOT EXISTS osm_abandoned_or_demolished_buildings (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_abandoned_or_demolished_buildings_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_abandoned_or_demolished_buildings_geom ON osm_abandoned_or_demolished_buildings USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_addr_point (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    name character varying,
    type character varying,
    ulica character varying,
    kod_ulic character varying,
    kod_simc character varying,
    kod_pna character varying,
    miejscowosc character varying,
    cz_msc character varying,
    geometry geometry(Point,4326),
    CONSTRAINT osm_addr_point_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_addr_point_geom ON osm_addr_point USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_addr_polygon (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    name character varying,
    type character varying,
    ulica character varying,
    kod_ulic character varying,
    kod_simc character varying,
    kod_pna character varying,
    miejscowosc character varying,
    cz_msc character varying,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_addr_polygon_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_addr_polygon_geom ON osm_addr_polygon USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_admin (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    admin_level integer,
    tags hstore,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_admin_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_admin_geom ON osm_admin USING gist (geometry);
-- make sure these are created manually after imposm data import
create index if not exists osm_admin_terc on osm_admin ((tags -> 'teryt:terc')) where exist(tags, 'teryt:terc');
create index if not exists osm_admin_simc on osm_admin ((tags -> 'teryt:simc')) where exist(tags, 'teryt:simc');

CREATE TABLE IF NOT EXISTS osm_adr (
    msc text,
    czmsc text,
    ul text,
    nr text,
    pna character varying,
    ulic character varying,
    simc character varying,
    geom geometry
);
CREATE INDEX IF NOT EXISTS osm_adr_geom ON osm_adr USING gist (geom);

CREATE TABLE IF NOT EXISTS osm_amenity_areas (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_amenity_areas_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_amenity_areas_geom ON osm_amenity_areas USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_amenity_points (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Point,4326),
    CONSTRAINT osm_amenity_points_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_amenity_points_geom ON osm_amenity_points USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_buildings (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    budynek character varying,
    kondygnacje character varying,
    ksztalt_dachu character varying,
    liczba_mieszkan character varying,
    kondygnacje_podziemne character varying,
    wysokosc_npg character varying,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_buildings_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_buildings_geom ON osm_buildings USING gist (geometry);


CREATE TABLE IF NOT EXISTS osm_hashed (
    hash text,
    geom geometry
);
CREATE INDEX IF NOT EXISTS osm_hashed_geom ON osm_hashed USING gist (geom);
CREATE INDEX IF NOT EXISTS osm_hashed_md5 ON osm_hashed USING btree (hash);

CREATE TABLE IF NOT EXISTS osm_place_areas (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_place_areas_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_place_areas_geom ON osm_place_areas USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_place_points (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Point,4326),
    CONSTRAINT osm_place_points_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_place_points_geom ON osm_place_points USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_roads (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(LineString,4326),
    CONSTRAINT osm_roads_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_roads_geom ON osm_roads USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_stats (
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    measurement_day date NOT NULL,
    metric_key text NOT NULL,
    metric_description text NOT NULL,
    value integer NOT NULL,
    sql_version integer DEFAULT 2,
    CONSTRAINT osm_stats_pk PRIMARY KEY (measurement_day, metric_key)
);

CREATE TABLE IF NOT EXISTS osm_tree_rows (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(LineString,4326),
    CONSTRAINT osm_tree_rows_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_tree_rows_geom ON osm_tree_rows USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_trees (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Point,4326),
    CONSTRAINT osm_trees_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_trees_geom ON osm_trees USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_waterareas (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_waterareas_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_waterareas_geom ON osm_waterareas USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_waterways (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(LineString,4326),
    CONSTRAINT osm_waterways_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_waterways_geom ON osm_waterways USING gist (geometry);

CREATE TABLE IF NOT EXISTS osm_woods (
    id integer NOT NULL,
    osm_id bigint NOT NULL,
    tags hstore,
    geometry geometry(Geometry,4326),
    CONSTRAINT osm_woods_pkey PRIMARY KEY (osm_id, id)
);
CREATE INDEX IF NOT EXISTS osm_woods_geom ON osm_woods USING gist (geometry);

-- -------------------------------------------------------------
