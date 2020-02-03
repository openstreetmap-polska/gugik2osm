insert into osm_hashed

    select md5(concat(lower(msc), coalesce(lower(ul), ''), nr)) hash, st_transform(geom, 2180) geom
    from osm_adr
    where geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)

    union all

    select md5(concat(lower(czmsc), coalesce(lower(ul), ''), nr)) hash, st_transform(geom, 2180) geom
    from osm_adr
    where geom && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
      and czmsc is not null
;