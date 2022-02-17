with
data as (
    select
        row_number() over() as way_id,
        geom_4326,
        GeometryType(geom_4326) geom_type,
        jsonb_strip_nulls(jsonb_build_object(
           'building', building,
           'amenity', amenity,
           'man_made', man_made,
           'leisure', leisure,
           'historic', historic,
           'tourism', tourism,
           'building:levels', building_levels,
           'source', 'www.geoportal.gov.pl'
        )) tags
    from bdot_buildings_all b
    where 1=1
        and ST_DWithin(b.geom_4326, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), 0.005)
        and ST_DistanceSphere(b.geom_4326, ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)) < %(search_distance)s
    order by b.geom_4326 <-> ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
    limit 1
),
points as (
    select
        way_id,
        geom_type,
        ST_DumpPoints(geom_4326) dp
    from data
),
polygon_outer_rings as (
    select
        way_id,
        geom_type,
        array_agg(ARRAY[st_y((dp).geom), st_x((dp).geom)]) as outer_ring
    from points
    where 1=1
        and geom_type = 'POLYGON'
        and (dp).path[1] = 1
    group by way_id, geom_type
),
polygon_inner_rings_temp as (
    select
        way_id,
        geom_type,
        array_agg(ARRAY[st_y((dp).geom), st_x((dp).geom)]) as inner_ring
    from points
    where 1=1
        and geom_type = 'POLYGON'
        and (dp).path[1] > 1
    group by way_id, geom_type, (dp).path[1]
),
polygon_inner_rings_final as (
    select
        way_id,
        geom_type,
        jsonb_agg(inner_ring) as inner_rings -- inner rings have different dimensionality so we can't use regular postgresql arrays
    from polygon_inner_rings_temp
    group by way_id, geom_type
),
multipolygon_outer_rings_temp as (
    select
        way_id,
        geom_type,
        array_agg(ARRAY[st_y((dp).geom), st_x((dp).geom)]) as outer_ring
    from points
    where 1=1
        and geom_type = 'MULTIPOLYGON'
        and (dp).path[2] = 1
    group by way_id, geom_type, (dp).path[1]
),
multipolygon_outer_rings_final as (
    select
        way_id,
        geom_type,
        array_agg(outer_ring) as outer_rings
    from multipolygon_outer_rings_temp
    group by way_id, geom_type
),
multipolygon_inner_rings_temp as (
    select
        way_id,
        geom_type,
        array_agg(ARRAY[st_y((dp).geom), st_x((dp).geom)]) as inner_ring
    from points
    where 1=1
        and geom_type = 'MULTIPOLYGON'
        and (dp).path[2] > 1
    group by way_id, geom_type, (dp).path[1], (dp).path[2]
),
multipolygon_inner_rings_final as (
    select
        way_id,
        geom_type,
        jsonb_agg(inner_ring) as inner_rings -- inner rings have different dimensionality so we can't use regular postgresql arrays
    from multipolygon_inner_rings_temp
    group by way_id, geom_type
)
select
    geom_type,
    tags,
    outer_ring,
    ARRAY[]::float[] as outer_rings,
    coalesce(inner_rings, '[]'::jsonb) inner_rings
from data
inner join polygon_outer_rings using(way_id, geom_type)
left join polygon_inner_rings_final using(way_id, geom_type)
union all
select
    geom_type,
    tags,
    null as outer_ring,
    outer_rings,
    coalesce(inner_rings, '[]'::jsonb) inner_rings
from data
inner join multipolygon_outer_rings_final using(way_id, geom_type)
left join multipolygon_inner_rings_final using(way_id, geom_type)
;
