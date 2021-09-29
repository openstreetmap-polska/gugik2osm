insert into bdot_buildings_all_new (
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
      when b.status_bdot = 'w budowie' then 'construction'
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
  where 1=1
    and b.status_bdot in ('eksploatowany', 'w budowie')
    and (b.koniecwersjiobiektu is null or b.koniecwersjiobiektu > CURRENT_TIMESTAMP)
;
