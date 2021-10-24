with
preprocessed_changesets as (
    select distinct on (changeset_id)
        changeset_id,
        st_transform(bbox, 4326) bbox,
        closed_at,
        uid,
        osm_user
    from changesets_processing.changesets c
    where 1=1
        and closed_at >= %(ts)s
        -- area less than 10 000 square kilometers
        and st_area(bbox) < 10000000000
),
preprocessed_osm as (
  select
    ST_Transform(ST_TileEnvelope(z, x, y), 4326) geom,
    to_char(created_at at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') created_at
  from expired_tiles
  where 1=1
    and created_at >= %(ts)s
    and file_name not like 'http_request%%'  -- psycopg2 requires 'escaping' of percent sign
  limit 100000
),
temp_osm as (
    select
        (st_dump(st_union(geom))).geom unioned_geom
    from preprocessed_osm
),
unioned_osm as (
    select
        row_number() over() rn,
        unioned_geom
    from temp_osm
),
joined_osm as (
    select
        u.rn,
        jsonb_agg(changeset) filter(where changeset is not null) changesets
    from unioned_osm u
    left join lateral (
        select
            jsonb_build_object(
                'changeset_id', changeset_id,
                'closed_at', closed_at,
                'uid', uid,
                'osm_user', osm_user
            ) changeset
        from preprocessed_changesets p
        where 1=1
            and u.unioned_geom && p.bbox
            and st_intersects(u.unioned_geom, p.bbox)
    ) t on true
    group by u.rn
),
osm as (
    select
        'osm' as dataset,
        ST_AsGeoJSON(u.unioned_geom)::jsonb bbox,
        coalesce(j.changesets, '[]'::jsonb) changesets
    from unioned_osm u
    left join joined_osm j using(rn)
),
-- todo: add unioning of geometry for package_exports too
prg as (
  select
    'exports' as dataset,
    ST_AsGeoJSON(ST_Transform(bbox, 4326))::jsonb bbox,
    to_char(created_at at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') created_at
  from package_exports
  where 1=1
    and created_at >= %(ts)s
    -- area less than 10 000 square kilometers
    and st_area(bbox) < 10000000000
)
select dataset, created_at, bbox, null::jsonb as changesets
from prg
union all
select dataset, null, bbox, changesets
from osm
;
