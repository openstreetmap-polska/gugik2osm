with
osm as (
  select
    'osm' as dataset,
    ST_AsGeoJSON(ST_Transform(ST_TileEnvelope(z, x, y), 4326))::jsonb bbox,
    to_char(created_at at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') created_at
  from expired_tiles
  where 1=1
    and created_at >= %(ts)s
    and file_name not like 'http_request%%'  -- psycopg2 requires 'escaping' of percent sign
), prg as (
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
select dataset, created_at, bbox
from osm
union all
select dataset, created_at, bbox
from prg
;
