with
building as (
    select
        geom_4326,
        jsonb_strip_nulls(jsonb_build_object(
           'building', building,
           'amenity', amenity,
           'man_made', man_made,
           'leisure', leisure,
           'historic', historic,
           'tourism', tourism,
           'building:levels', building_levels,
           'source:building', 'BDOT'
        )) tags
    from bdot_buildings_all b
    where 1=1
        and ST_DWithin(b.geom_4326, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), 0.005)
        and ST_DistanceSphere(b.geom_4326, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)) < %(search_distance)s
    order by b.geom_4326 <-> ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
    limit 1
)
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(ST_AsGeoJSON(building.*, 'geom_4326', 6)::json)
)
FROM building
;
