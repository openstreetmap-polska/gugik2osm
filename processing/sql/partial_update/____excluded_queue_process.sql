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

with b_ids as (
  delete from exclude_bdot_buildings_queue
  where processed = false
  returning id
),
delete_tiles as (
  delete from tiles t
  using bdot_buildings b, b_ids
  where 1=1
    and z >= 13
    and t.bbox && st_transform(b.geom_4326, 3857)
    and b.lokalnyid = b_ids.id
)
insert into exclude_bdot_buildings (id)
  select id
  from b_ids
on conflict do nothing
;
