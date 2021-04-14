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
where d.lokalnyid in %s
limit 50000
;
