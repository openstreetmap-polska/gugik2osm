create table if not exists tiles_bounds (
    z int,
    x int,
    y int,
    geom_3857 geometry(Polygon, 3857),
    primary key (z, x, y)
);

create index if not exists idx_tiles_bounds_geom on tiles_bounds using gist (geom_3857);

cluster tiles_bounds using idx_tiles_bounds_geom;
