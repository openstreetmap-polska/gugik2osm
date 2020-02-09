insert into prg.delta
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
    where
        -- make sure given bounding box is valid
        ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
        and
        prg.geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
        and
        osm.hash is null
;
