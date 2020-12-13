insert into package_exports (
    bbox,
    adresy,
    budynki
)
values (
    st_transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 4326), 3857),
    %(lb_adresow)s,
    %(lb_budynkow)s
);
