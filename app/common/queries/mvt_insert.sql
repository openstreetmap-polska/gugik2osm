insert into tiles (mvt, z, x, y, bbox)
  select mvt(z, x, y), z, x, y, ST_TileEnvelope(z, x, y) from (
    select %(z)s as z, %(x)s as x, %(y)s as y
  ) t
on conflict do nothing
;
