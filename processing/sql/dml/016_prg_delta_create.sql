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
    from prg.pa_hashed prg
    join prg.pa using (lokalnyid)
    left join osm_hashed osm
        on (prg.hash = osm.hash and st_dwithin(prg.geom, osm.geom, 50))
    where osm.hash is null
;
create index if not exists delta_gis on prg.delta using gist (geom);
cluster prg.delta using delta_gis;
create index if not exists delta_lokalnyid on prg.delta using btree (lokalnyid);
