with
data as (
  select
    'osm' as dataset,
    ST_AsGeoJSON(ST_Transform(ST_TileEnvelope(z, x, y), 4326))::jsonb bbox,
    to_char(created_at at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') created_at
  from expired_tiles
  where 1=1
    and created_at is not null
    and created_at >= %(ts)s
    and file_name not like 'http_request%'
    -- bbox is more or less in Poland
    and ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_TileEnvelope(z, x, y)

  union all

  select
    'exports' as dataset,
    ST_AsGeoJSON(ST_Transform(bbox, 4326))::jsonb bbox,
    to_char(created_at at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') created_at
  from package_exports
  where 1=1
    and created_at is not null
    and created_at >= %(ts)s
    -- area less than 10 000 square kilometers
    and st_area(bbox) < 10000000000
)
select dataset, created_at, bbox
from data
;
