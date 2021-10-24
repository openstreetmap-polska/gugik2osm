alter table tiles rename to tiles_old;
alter table tiles_new rename to tiles;
alter index idx_tiles_bbox rename to idx_tiles_bbox_old;
alter index idx_tiles_bbox_new rename to idx_tiles_bbox;
