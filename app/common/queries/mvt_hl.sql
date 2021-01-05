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
        left join exclude_prg on d.lokalnyid = exclude_prg.id
        where d.geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
            and exclude_prg.id is null
        limit 500000
    ),
    b as (
        select
            lokalnyid,
            ST_AsMVTGeom(ST_Transform(geom_4326, 3857), ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)::box2d) geom,
            status_bdot,
            kategoria_bdot,
            funkcja_ogolna_budynku,
            funkcja_szczegolowa_budynku,
            aktualnosc_geometrii,
            aktualnosc_atrybutow,
            building,
            amenity,
            man_made,
            leisure,
            historic,
            tourism,
            building_levels
        from bdot_buildings b
        left join exclude_bdot_buildings ex on b.lokalnyid=ex.id
        where geom_4326 && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 4326)
            and ex.id is null
        limit 500000
    ),
    result as (
        select
            (select ST_AsMVT(a.*, 'prg2load') from a) || (select ST_AsMVT(b.*, 'buildings') from b) mvt,
            %(z)s z,
            %(x)s x,
            %(y)s y,
            ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857) bbox
    )
    select * from result
on conflict do nothing
;
