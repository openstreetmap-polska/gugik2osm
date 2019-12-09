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
