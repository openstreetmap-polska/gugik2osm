insert into bdot_buildings_new (
    powiat,
    lokalnyid,
    status_bdot,
    kategoria_bdot,
    funkcja_ogolna_budynku,
    funkcja_szczegolowa_budynku,
    aktualnosc_geometrii,
    aktualnosc_atrybutow,
    building,
    amenity,
    man_made,
    leisure,
    historic,
    tourism,
    building_levels,
    geom_4326
)
  select
    powiat,
    lokalnyid,
    status_bdot,
    kategoria_bdot,
    funkcja_ogolna_budynku,
    funkcja_szczegolowa_budynku,
    aktualnosc_geometrii,
    aktualnosc_atrybutow,
    building,
    amenity,
    man_made,
    leisure,
    historic,
    tourism,
    building_levels,
    geom_4326
  from bdot_buildings_all_new b
  left join lateral (
    select 1 as exsts
    from osm_buildings osm
    where 1=1
      and osm.geometry && b.geom_4326
      and st_intersects(osm.geometry, b.geom_4326) limit 1
  ) o on true
  left join lateral (
    select 1 as exsts
    from osm_abandoned_or_demolished_buildings osm
    where 1=1
      and osm.geometry && b.geom_4326
      and st_intersects(osm.geometry, b.geom_4326) limit 1
  ) o2 on true
  left join exclude_bdot_buildings ex on ex.id=b.lokalnyid
  where 1=1
    and o.exsts is null
    and o2.exsts is null
    and ex.id is null
;
