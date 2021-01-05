drop table if exists bdot_buildings_new;
create table if not exists bdot_buildings_new (
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
    geom_4326 geometry(polygon, 4326) not null
);
