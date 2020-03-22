insert into tiles (mvt, z, x, y, bbox)
    with a as (
        select
           ST_AsMVTGeom(
             ST_Transform(d.geom, 3857),
             ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)::box2d
           ) geom
        from prg.delta d
        where d.geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
        limit 500000
    )
    select
        ST_AsMVT(a.*, 'prg2load_geomonly') mvt,
        %(z)s z,
        %(x)s x,
        %(y)s y,
        ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857) bbox
    from a
returning mvt
;
