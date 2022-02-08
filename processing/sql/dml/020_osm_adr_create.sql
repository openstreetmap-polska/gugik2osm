set jit=on;

drop table if exists osm_adr;
create table osm_adr as
with
tab as (
    select
      miejscowosc,
      cz_msc,
      ulica,
      ltrim(rtrim(replace(replace(upper(trim(type)), '\', '/'), ' ', ''), './'), '.0/') as nr_porzadkowy,
      kod_pna,
      kod_ulic,
      kod_simc,
      ST_Centroid(geometry) geom
    from osm_addr_polygon
    union all
    select
      miejscowosc,
      cz_msc,
      ulica,
      ltrim(rtrim(replace(replace(upper(trim(type)), '\', '/'), ' ', ''), './'), '.0/') as nr_porzadkowy,
      kod_pna,
      kod_ulic,
      kod_simc,
      geometry
    from osm_addr_point
),
a as (
    select
      case when miejscowosc = '' then null else trim(miejscowosc) end msc,
      case when cz_msc = '' then null else trim(cz_msc) end czmsc,
      case when ulica = '' then null else trim(ulica) end ul,
      nr_porzadkowy as nr,
      case when kod_pna ~ '^\d{2}-\d{3}$' and kod_pna <> '00-000' then kod_pna else null end pna,
      case when kod_ulic ~ '^\d{5}$' then kod_ulic else null end ulic,
      case when kod_simc ~ '^\d{7}$' then kod_simc else null end simc,
      geom
    from tab
)
SELECT
  a.*
FROM a
where
-- removed this condition as some addresses don't have either addr:city nor addr:place tags
--  coalesce(msc, czmsc) is not null
--  and
  nr is not null
;
