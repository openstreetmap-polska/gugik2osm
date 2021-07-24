with
preprocess_1 as (
    select
        st_linemerge(geom_2180) geom_2180,
        coalesce(osm_street_name, street_name) "name"
    from streets_all s
    left join street_names_mappings m on s.interpolated_teryt_simc=m.teryt_simc_code and s.teryt_ulic=m.teryt_ulic_code
    where 1=1
        and geom_2180 && st_transform(ST_GeomFromGeoJSON( %(geojson_geometry)s ), 2180)
        and st_intersects(geom_2180, st_transform(ST_GeomFromGeoJSON( %(geojson_geometry)s ), 2180))
    limit 50000
),
preprocess_2 as (
    select
        (st_dump(geom_2180)).geom geom_2180,
        jsonb_build_object(
            'name', name
        ) tags
    from preprocess_1
),
data as (
    select
        row_number() over() as way_id,
        st_transform(geom_2180, 4326) geom_4326,
        GeometryType(geom_2180) geom_type,
        tags
    from preprocess_2
),
points as (
    select
        way_id,
        ST_DumpPoints(geom_4326) dp
    from data
),
coordinates as (
    select
        way_id,
        array_agg(ARRAY[st_y((dp).geom), st_x((dp).geom)]) as list_of_coordinate_pairs
    from points
    group by way_id
)
select
    geom_type,
    tags,
    list_of_coordinate_pairs
from data
inner join coordinates using(way_id)
;
