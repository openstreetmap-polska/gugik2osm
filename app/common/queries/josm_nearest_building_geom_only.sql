select
    ST_AsGeoJSON(geom_4326, 6) geojson
from bdot_buildings_all b
where 1=1
    and ST_DWithin(b.geom_4326, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), 0.005)
    and ST_DistanceSphere(b.geom_4326, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)) < %(search_distance)s
order by b.geom_4326 <-> ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)  --
limit 1
;
