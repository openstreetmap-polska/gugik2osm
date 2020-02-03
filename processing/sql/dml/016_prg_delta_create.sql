drop table if exists prg.delta;
create unlogged table prg.delta as
    select
        pa.lokalnyid,
        pa.teryt_msc,
        pa.teryt_simc,
        pa.teryt_ulica,
        pa.teryt_ulic,
        pa.nr,
        pa.pna,
        pa.gml geom
    from prg.pa
    join prg.pa_hashed prg using (lokalnyid)
    left join osm_hashed osm
        on (prg.hash = osm.hash and st_dwithin(st_transform(prg.geom, 2180), st_transform(osm.geom, 2180), 50))
    where osm.hash is null
;
create index if not exists delta_gis on prg.delta using gist (geom);
cluster prg.delta using delta_gis;
alter table prg.delta set logged;
