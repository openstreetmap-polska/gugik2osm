insert into exclude_bdot_buildings_queue ( id )
    select lokalnyid
    from bdot_buildings b
    where 1=1
        and b.geom_4326 && ST_GeomFromGeoJSON( %(geojson_geometry)s )
        and st_intersects(b.geom_4326, ST_GeomFromGeoJSON( %(geojson_geometry)s ))
on conflict do nothing;
