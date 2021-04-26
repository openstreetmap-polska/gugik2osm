with
exp as (
  update expired_tiles
  set processed = true
  where processed = false
  returning z, x, y
),
exp_bounds as (
  select distinct ST_TileEnvelope(z, x, y) as geom from exp
),
osm_adr_delete as (
  delete from osm_adr
  using exp_bounds
  where
    -- make sure given bounding box is valid
    ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
    and
    osm_adr.geom && ST_Transform(exp_bounds.geom, 4326)
),
osm_adr_insert as (
  insert into osm_adr
  SELECT a.*
  FROM (
    select
      case when miejscowosc = '' then null else trim(miejscowosc) end msc,
      case when cz_msc = '' then null else trim(cz_msc) end czmsc,
      case when ulica = '' then null else trim(ulica) end ul,
      nr_porzadkowy as nr,
      case when kod_pna ~ '^\d{2}-\d{3}$' and kod_pna <> '00-000' then kod_pna else null end pna,
      case when kod_ulic ~ '^\d{5}$' then kod_ulic else null end ulic,
      case when kod_simc ~ '^\d{7}$' then kod_simc else null end simc,
      geom
    from (
      select miejscowosc, cz_msc, ulica, type as nr_porzadkowy, kod_pna, kod_ulic, kod_simc, ST_Centroid(geometry) geom
      from osm_addr_polygon
      join exp_bounds
        on geometry && ST_Transform(exp_bounds.geom, 4326) and ST_Centroid(geometry) && ST_Transform(exp_bounds.geom, 4326)
      where
        -- make sure given bounding box is valid
        ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom

      union all

      select miejscowosc, cz_msc, ulica, type as nr_porzadkowy, kod_pna, kod_ulic, kod_simc, geometry
      from osm_addr_point
      join exp_bounds on geometry && ST_Transform(exp_bounds.geom, 4326)
      where
        -- make sure given bounding box is valid
        ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
    ) tab
  ) a
  where
  -- removed this condition as some addresses don't have neither addr:city nor addr:place tags
  --  coalesce(msc, czmsc) is not null
  --  and
    nr is not null
),
osm_hashed_delete as (
  delete from osm_hashed
  using exp_bounds
  where
    -- make sure given bounding box is valid
    ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
    and
    osm_hashed.geom && ST_Transform(exp_bounds.geom, 2180)
),
osm_hashed_insert as (
  insert into osm_hashed
    select md5(concat(lower(msc), coalesce(lower(ul), ''), nr)) hash, st_transform(osm_adr.geom, 2180) geom
    from osm_adr
    join exp_bounds on osm_adr.geom && ST_Transform(exp_bounds.geom, 4326)
    where
      -- make sure given bounding box is valid
      ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom

    union all

    select md5(concat(lower(czmsc), coalesce(lower(ul), ''), nr)) hash, st_transform(osm_adr.geom, 2180) geom
    from osm_adr
    join exp_bounds on osm_adr.geom && ST_Transform(exp_bounds.geom, 4326)
    where
      -- make sure given bounding box is valid
      ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
      and
      czmsc is not null
),
prg_delta_delete as (
  delete from prg.delta d
  using exp_bounds
  where
    -- make sure given bounding box is valid
    ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
    and
    d.geom && ST_Transform(exp_bounds.geom, 2180)
    and (
      exists (
        select 1
        from prg.pa_hashed prg, osm_hashed osm
        where
          st_dwithin(prg.geom, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          st_dwithin(osm.geom, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          d.lokalnyid = prg.lokalnyid
          and
          prg.hash = osm.hash
          and
          st_dwithin(prg.geom, osm.geom, 150)
      )
      or
      exists (
        select 1
        from prg.pa_hashed prg, osm_hashed osm
        where
          st_dwithin(prg.geom, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          st_dwithin(osm.geom, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          d.lokalnyid = prg.lokalnyid
          and
          st_dwithin(prg.geom, osm.geom, 2)
      )
      or
      exists (
        select 1
        from osm_adr osm
        where
          st_dwithin(osm.geom, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          st_dwithin(d.geom, st_transform(osm.geom, 2180), 40) and d.nr_standaryzowany = osm.nr
      )
      or
      exists (
        select 1
        from osm_addr_polygon osm
        where
          st_dwithin(osm.geometry, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          st_intersects(d.geom, st_transform(osm.geometry, 2180)) AND (osm.type = d.nr_standaryzowany) -- type = nr
      )
      or
      exists (
        select 1
        from osm_addr_polygon osm
        where
          st_dwithin(osm.geometry, ST_Transform(exp_bounds.geom, 2180), 150)
          and
          st_dwithin(d.geom, st_transform(osm.geometry, 2180), 15) AND (osm.type = d.nr_standaryzowany) -- type = nr
      )
    )
),
bdot_buildings_delete as (
  delete from bdot_buildings b
  using osm_buildings o, exp_bounds
  where
    -- make sure given bounding box is valid
    ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
    and
    b.geom_4326 && ST_Transform(exp_bounds.geom, 4326)
    and
    o.geometry && ST_Transform(exp_bounds.geom, 4326)
    and
    st_intersects(b.geom_4326, o.geometry)
),
tiles_to_update as (
  select distinct z, x, y
  from tiles_bounds
  join exp_bounds on tiles_bounds.geom_3857 && exp_bounds.geom
  where z >= 8
)
update tiles
set mvt = mvt(tiles.z, tiles.x, tiles.y)
from tiles_to_update
where 1=1
  and tiles_to_update.z = tiles.z
  and tiles_to_update.x = tiles.x
  and tiles_to_update.y = tiles.y
;
