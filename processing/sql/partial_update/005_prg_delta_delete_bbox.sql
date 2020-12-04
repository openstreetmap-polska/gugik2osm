delete from prg.delta d
where
  -- make sure given bounding box is valid
  ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
  and
  d.geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
  and (
    exists (
      select 1
      from prg.pa_hashed prg, osm_hashed osm
      where
        st_dwithin(prg.geom, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        st_dwithin(osm.geom, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        d.lokalnyid = prg.lokalnyid
        and
        prg.hash = osm.hash
        and
        st_dwithin(prg.geom, osm.geom, 150)
    )
    or
    exists (
      select 1
      from prg.pa_hashed prg, osm_hashed osm
      where
        st_dwithin(prg.geom, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        st_dwithin(osm.geom, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        d.lokalnyid = prg.lokalnyid
        and
        st_dwithin(prg.geom, osm.geom, 5)
    )
    or
    exists (
      select 1
      from osm_adr osm
      where
        st_dwithin(osm.geom, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        st_dwithin(d.geom, st_transform(osm.geom, 2180), 40) and d.nr_standaryzowany = osm.nr
    )
    or
    exists (
      select 1
      from osm_addr_polygon osm
      where
        st_dwithin(osm.geometry, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        st_intersects(d.geom, st_transform(osm.geometry, 2180)) AND (osm.name = d.nr_standaryzowany) -- name = nr
    )
    or
    exists (
      select 1
      from osm_addr_polygon osm
      where
        st_dwithin(osm.geometry, ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180), 150)
        and
        st_dwithin(d.geom, st_transform(osm.geometry, 2180), 15) AND (osm.name = d.nr_standaryzowany) -- name = nr
    )
  )
;
