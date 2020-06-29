delete from tiles t
using prg.delta d
where 1=1
    and z >= 13
    and t.bbox && st_transform(d.geom, 3857)
    and d.lokalnyid in %s
;
