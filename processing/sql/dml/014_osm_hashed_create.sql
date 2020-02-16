drop table if exists osm_hashed;
create unlogged table osm_hashed as
    select md5(concat(lower(msc), coalesce(lower(ul), ''), nr)) hash, st_transform(geom, 2180) geom
    from osm_adr
    union all
    select md5(concat(lower(czmsc), coalesce(lower(ul), ''), nr)) hash, st_transform(geom, 2180) geom
    from osm_adr
    where czmsc is not null
;
