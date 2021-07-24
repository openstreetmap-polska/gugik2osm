insert into exclude_prg_queue ( id )
    select lokalnyid
    from prg.delta d
    where 1=1
        and d.geom && st_transform(ST_GeomFromGeoJSON( %(geojson_geometry)s ), 2180)
        and st_intersects(d.geom, st_transform(ST_GeomFromGeoJSON( %(geojson_geometry)s ), 2180))
on conflict do nothing;
