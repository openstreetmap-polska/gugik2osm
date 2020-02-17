delete from prg.lod1_buildings a
where exists (
        select 1
        from osm_buildings o
        where st_intersects(a.geom, o.geometry)
      )
;