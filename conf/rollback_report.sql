with
obszar (geometry) as (
select st_geomfromgeojson('{"coordinates":[[[22.12039233187417,51.71894479222061],[22.254875757457512,51.82815005515735],[22.18851648184173,51.83774747024492],[22.076976422828125,51.816805018406086],[22.001792775454618,51.73577961852129],[22.014146895914934,51.701666181399474],[22.101331688878275,51.712821482728],[22.12039233187417,51.71894479222061]]],"type":"Polygon"}')
),
budynki as (
select b.lokalnyid, b.geom_4326
from bdot_buildings_all b
join obszar on obszar.geometry && b.geom_4326 and st_intersects(obszar.geometry, b.geom_4326)
),
adresy as (
select a.lokalnyid, a.geom_2180
from addresses a
join obszar on st_transform(obszar.geometry, 2180) && a.geom_2180 and st_intersects(st_transform(obszar.geometry, 2180), a.geom_2180)
),
dd1 as (
delete from exclude_bdot_buildings eb
using budynki b
where eb.id=b.lokalnyid and eb.created_at > now() - interval '24 hour'
returning id
),
dd2 as (
delete from exclude_prg ea
using adresy a
where ea.id=a.lokalnyid and ea.created_at > now() - interval '24 hour'
returning id
),
zxy as (
select distinct z, x, y
from adresy a
join tiles_bounds t on geom_3857 && st_transform(geom_2180, 3857) and st_intersects(geom_3857, st_transform(geom_2180, 3857))
where z >= 8
union
select distinct z, x, y
from budynki b
join tiles_bounds t on geom_3857 && st_transform(geom_4326, 3857) and st_intersects(geom_3857, st_transform(geom_4326, 3857))
where z >= 8
),
uu1 as (
update tiles t
set mvt = mvt(t.z, t.x, t.y)
from zxy
where t.z=zxy.z and t.x=zxy.x and t.y=zxy.y
returning t.z, t.x, t.y
)
select 'adresy' warstwa, count(*) from dd2
union all
select 'budynki', count(*) from dd1
union all
select 'kafelki', count(*) from uu1
;