select
    lokalnyid::text as id,
    building,
    amenity,
    man_made,
    leisure,
    historic,
    tourism,
    building_levels,
    ST_AsGeoJSON(geom_4326, 6) geom
from bdot_buildings b
left join exclude_bdot_buildings ex on b.lokalnyid=ex.id
where 1=1
    and b.geom_4326 && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
    and ex.id is null
limit 50000
