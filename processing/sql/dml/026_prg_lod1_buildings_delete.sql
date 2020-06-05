delete from prg.lod1_buildings a
using osm_buildings o, exclude_lod1 lod1
where st_intersects(a.geom, o.geometry) or lod1.id = a.id
;
analyze prg.lod1_buildings;
