delete from prg.lod1_buildings a
using osm_buildings o
where st_intersects(a.geom, o.geometry)
;