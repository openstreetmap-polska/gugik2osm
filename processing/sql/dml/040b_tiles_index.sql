create index if not exists idx_tiles_bbox_new on tiles_new using gist (bbox);
cluster tiles_new using idx_tiles_bbox_new;
alter table tiles_new add primary key (z, x, y);
analyze tiles_new;
