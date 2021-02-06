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
    b.powiat,
    b.lokalnyid,
    b.status_bdot,
    b.kategoria_bdot,
    b.funkcja_ogolna_budynku,
    b.funkcja_szczegolowa_budynku,
    b.aktualnosc_geometrii,
    b.aktualnosc_atrybutow,
    case
      when coalesce(building, amenity, man_made, leisure, historic, tourism) is null then 'yes'
      else m.building
    end building,
    m.amenity,
    m.man_made,
    m.leisure,
    case
      when b.zabytek in ('true', 't') then 'yes'
      else m.historic
    end historic,
    m.tourism,
    b.liczba_kondygnacji as building_levels,
    st_transform(b.geom_a_2180, 4326) as geom_4326
  from bdot.v_bubd_a b
  left join bdot.buildings_categories_mappings m
    on m.kategoria_bdot=b.kategoria_bdot
      and m.funkcja_ogolna_budynku=coalesce(b.funkcja_ogolna_budynku, '')
      and m.funkcja_szczegolowa_budynku=coalesce(b.funkcja_szczegolowa_budynku, '')
  left join lateral (
    select 1 as exsts
    from osm_buildings osm
    where 1=1
      and osm.geometry && st_transform(b.geom_a_2180, 4326)
      and st_intersects(osm.geometry, st_transform(b.geom_a_2180, 4326)) limit 1
  ) o on true
  left join exclude_bdot_buildings ex on ex.id=b.lokalnyid
  where 1=1
    and b.status_bdot in ('eksploatowany', 'w budowie')
    and (b.koniecwersjiobiektu is null or b.koniecwersjiobiektu > CURRENT_TIMESTAMP)
    and o.exsts is null
    and ex.id is null
;
--
--insert into bdot_buildings_new (
--    powiat,
--    lokalnyid,
--    status_bdot,
--    kategoria_bdot,
--    funkcja_ogolna_budynku,
--    funkcja_szczegolowa_budynku,
--    aktualnosc_geometrii,
--    aktualnosc_atrybutow,
--    building,
--    amenity,
--    man_made,
--    leisure,
--    historic,
--    tourism,
--    building_levels,
--    geom_4326
--)
--  select
--    b.powiat,
--    b.lokalnyid,
--    b.status_bdot,
--    b.kategoria_bdot,
--    b.funkcja_ogolna_budynku,
--    b.funkcja_szczegolowa_budynku,
--    b.aktualnosc_geometrii,
--    b.aktualnosc_atrybutow,
--    coalesce(m.building, 'yes') building,
--    m.amenity,
--    m.man_made,
--    m.leisure,
--    case
--      when b.zabytek in ('true', 't') then 'yes'
--      else m.historic
--    end historic,
--    m.tourism,
--    b.liczba_kondygnacji as building_levels,
--    st_transform(b.geom_a_2180, 4326) as geom_4326
--  from bdot.v_bubd_a b
--  left join bdot.buildings_categories_mappings m
--    on m.kategoria_bdot=b.kategoria_bdot
--      and m.funkcja_ogolna_budynku=b.funkcja_ogolna_budynku
--      and m.funkcja_szczegolowa_budynku=coalesce(b.funkcja_szczegolowa_budynku, '')
--  left join exclude_bdot_buildings ex on ex.id=b.lokalnyid
--  where 1=1
--    and b.status_bdot in ('eksploatowany', 'w budowie')
--    and (b.koniecwersjiobiektu is null or b.koniecwersjiobiektu > CURRENT_TIMESTAMP)
--    and ex.id is null
--    and not exists (
--        select 1 as exsts
--        from osm_buildings osm
--        where 1=1
--          and osm.geometry && st_transform(b.geom_a_2180, 4326)
--          and st_intersects(osm.geometry, st_transform(b.geom_a_2180, 4326))
--    )
--;
