drop table if exists tiles_new;
create table tiles_new as
  select
    z, x, y,
    ST_TileEnvelope(z, x, y) as bbox,
    mvt(z, x, y) as mvt
  from tiles
;
