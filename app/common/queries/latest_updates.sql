with
data as (
  select
    'osm' as dataset,
    -- in postgis 3.0 there is a function to get bbox for xyz tile
    -- ST_TileEnvelope(z, x, y) bbox,
    ST_AsGeoJSON(ST_Transform(ST_MakeEnvelope(
        -20037508.34 + (x * (20037508.34*2)/(2^z)),
        20037508.34 - (y * (20037508.34*2)/(2^z)),
        -20037508.34 + (x * (20037508.34*2)/(2^z)) + (20037508.34*2)/(2^z),
        20037508.34 - (y * (20037508.34*2)/(2^z)) - (20037508.34*2)/(2^z),
        3857
    ), 4326))::jsonb bbox,
    to_char(created_at at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') created_at
  from expired_tiles
  where 1=1
    and created_at is not null
    and created_at >= %(ts)s
    -- bbox is more or less in Poland
    and ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(
        -20037508.34 + (x * (20037508.34*2)/(2^z)),
        20037508.34 - (y * (20037508.34*2)/(2^z)),
        -20037508.34 + (x * (20037508.34*2)/(2^z)) + (20037508.34*2)/(2^z),
        20037508.34 - (y * (20037508.34*2)/(2^z)) - (20037508.34*2)/(2^z),
        3857
    )

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
