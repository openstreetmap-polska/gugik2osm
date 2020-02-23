create table if not exists tiles (
	z integer not null,
	x integer not null,
	y integer not null,
	mvt bytea,
	bbox geometry(Polygon, 3857),
	constraint tiles_zxy_pk primary key (z, x, y)
);

create index if not exists idx_tiles_bbox on tiles using gist (bbox);
