insert into tiles (mvt, z, x, y, bbox)
    with a as (
        select
           d.lokalnyid,
           d.teryt_msc,
           d.teryt_simc,
           d.teryt_ulica,
           d.teryt_ulic,
           d.nr,
           d.pna,
           ST_AsMVTGeom(
             ST_Transform(d.geom, 3857),
             ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)::box2d
           ) geom
        from prg.delta d
        where d.geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
        limit 500000
    ),
    b as (
        select
        ST_AsMVTGeom(ST_Transform(geom, 3857), ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)::box2d) geom
        from prg.lod1_buildings
        where geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 4326)
        limit 500000
    ),
    result as (
        select
            (select ST_AsMVT(a.*, 'prg2load') from a) || (select ST_AsMVT(b.*, 'lod1_buildings') from b) mvt,
            %(z)s z,
            %(x)s x,
            %(y)s y,
            ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857) bbox
    )
    select * from result
on conflict do nothing
;
