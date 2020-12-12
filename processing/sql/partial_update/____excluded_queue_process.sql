with prg_ids as (
  delete from exclude_prg_queue
  where processed = false
  returning id
),
delete_tiles as (
  delete from tiles t
  using prg.delta d, prg_ids prg
  where 1=1
    and z >= 13
    and t.bbox && st_transform(d.geom, 3857)
    and d.lokalnyid = prg.id
)
insert into exclude_prg (id)
  select id
  from prg_ids
on conflict do nothing
;

with lod1_ids as (
  delete from exclude_lod1_queue
  where processed = false
  returning id
),
delete_tiles as (
  delete from tiles t
  using prg.lod1_buildings b, lod1_ids
  where 1=1
    and z >= 13
    and t.bbox && st_transform(b.geom, 3857)
    and b.id = lod1_ids.id
)
insert into exclude_lod1 (id)
  select id
  from lod1_ids
on conflict do nothing
;
