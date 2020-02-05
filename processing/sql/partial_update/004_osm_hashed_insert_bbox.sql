insert into osm_hashed

    select md5(concat(lower(msc), coalesce(lower(ul), ''), nr)) hash, st_transform(geom, 2180) geom
    from osm_adr
    where
      -- make sure given bounding box is valid
      ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
      and
      geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 4326)

    union all

    select md5(concat(lower(czmsc), coalesce(lower(ul), ''), nr)) hash, st_transform(geom, 2180) geom
    from osm_adr
    where
      -- make sure given bounding box is valid
      ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
      and
      geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 4326)
      and czmsc is not null
;