delete from tiles t
using prg.lod1_buildings l
where 1=1
    and z >= 13
    and t.bbox && st_transform(l.geom, 3857)
    and l.id in %s
;
