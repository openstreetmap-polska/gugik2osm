delete from prg.lod1_buildings a
using exclude_lod1 lod1
where lod1.id = a.id
;
