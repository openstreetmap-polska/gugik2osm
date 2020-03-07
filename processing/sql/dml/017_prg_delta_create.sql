drop table if exists prg.delta_new;
create unlogged table prg.delta_new as
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
create index if not exists delta_gis_new on prg.delta_new using gist (geom);
cluster prg.delta_new using delta_gis_new;
create index if not exists delta_lokalnyid_new on prg.delta_new using btree (lokalnyid);
