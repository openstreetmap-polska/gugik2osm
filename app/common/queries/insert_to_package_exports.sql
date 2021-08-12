insert into package_exports (
    bbox,
    adresy,
    budynki
)
values (
    st_transform(ST_GeomFromGeoJSON( %(geojson_geometry)s ), 3857),
    %(lb_adresow)s,
    %(lb_budynkow)s
);
