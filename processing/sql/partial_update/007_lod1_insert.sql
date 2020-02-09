insert into prg.lod1_buildings
    select ST_Transform(a.geom, 4326)
    from public.lod1_buildings a
    where
      -- make sure given bounding box is valid
      ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
      and
      a.geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
      and not exists (
        select 1
        from osm_buildings o
        where st_intersects(ST_Transform(a.geom, 4326), o.geometry)
      )
;