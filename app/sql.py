sql_where_bbox = '''
select
   d.lokalnyid,
   d.teryt_msc,
   d.teryt_simc,
   d.teryt_ulica,
   d.teryt_ulic,
   d.nr,
   d.pna,
   st_x(st_transform(d.geom, 4326)) x4326,
   st_y(st_transform(d.geom, 4326)) y4326
from prg.delta d
where d.geom && st_transform(ST_MakeEnvelope(%s, %s, %s, %s, 4326), 2180)
limit 50000
'''

sql_buildings_where_bbox = '''
select 
    way_id, 
    array_agg(ARRAY[cast(st_x((dp).geom) as numeric(10, 8)), cast(st_y((dp).geom) as numeric(10, 8))]) as arr
from (
    select row_number() over() * -1 - 100000 as way_id, ST_DumpPoints(geom) dp
    from prg.lod1_buildings
    where geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326) 
    limit 50000
) a
group by way_id
'''

sql_mvt = '''
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
    )
    select 
        (select ST_AsMVT(a.*, 'prg2load') from a) || (select ST_AsMVT(b.*, 'lod1_buildings') from b) mvt,
        %(z)s z,
        %(x)s x,
        %(y)s y,
        ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857) bbox
returning mvt
'''

sql_mvt_ll = '''
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
'''

sql_delta_point_info = '''
select
   lokalnyid,
   teryt_msc,
   teryt_simc,
   teryt_ulica,
   teryt_ulic,
   nr,
   pna
from prg.delta
where lokalnyid = cast(%s as uuid)
'''

sql_get_mvt_by_zxy = '''
select mvt
from tiles
where z = %s and x = %s and y = %s
'''
