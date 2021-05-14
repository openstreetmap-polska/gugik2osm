with
a as (
    select
        row_number() over() * -1 - 100000 as way_id,
        -- holes in polygons are too difficult :(
        ST_MakePolygon(ST_ExteriorRing(geom_4326)) geom_4326,
        building,
        amenity,
        man_made,
        leisure,
        historic,
        tourism,
        building_levels
    from bdot_buildings_all b
    where 1=1
        and b.geom_4326 && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
    limit 50000
),
b as (
    select
        way_id,
        ST_DumpPoints(geom_4326) dp
    from a
),
c as (
    select
        way_id,
        array_agg(ARRAY[cast(st_x((dp).geom) as numeric(10, 8)), cast(st_y((dp).geom) as numeric(10, 8))]) as arr
    from b
    group by way_id
),
d as (
    select
        way_id,
        arr,
        building,
        amenity,
        man_made,
        leisure,
        historic,
        tourism,
        building_levels
    from c
    join a using(way_id)
)
select * from d;
