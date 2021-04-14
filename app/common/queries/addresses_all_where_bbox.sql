select
   d.lokalnyid,
   d.teryt_msc,
   d.teryt_simc,
   d.teryt_ulica,
   d.teryt_ulic,
   d.nr,
   d.pna,
   st_x(st_transform(d.geom_2180, 4326)) x4326,
   st_y(st_transform(d.geom_2180, 4326)) y4326
from addresses d
where d.geom_2180 && st_transform(ST_MakeEnvelope(%s, %s, %s, %s, 4326), 2180)
limit 50000
;
