set jit=on;

insert into streets_all_new
select street_id, interpolated_teryt_simc, teryt_ulic, street_name, geom_2180 --st_astext(st_transform(geom_2180, 4326))
from (
  select
    lokalnyid::uuid street_id,
    idteryt teryt_ulic,
    nazwaglownaczesc street_name,
    ST_GeomFromGML((xpath('/geometry/*', geometry::xml))[1]::text) geom_2180
  from prg.ulice
  where 1=1
    and (koniecwersjiobiektu is null or koniecwersjiobiektu::timestamptz > CURRENT_TIMESTAMP)
    and (waznydo is null or waznydo::date > CURRENT_DATE)
    and geometry is not null
    and is_parsable_gml((xpath('/geometry/*', geometry::xml))[1]::text)
) u
left join lateral (
  select teryt_simc interpolated_teryt_simc
  from (
    select teryt_simc, count(*) cnt
    from (
      select teryt_simc from addresses a where st_dwithin(a.geom_2180, u.geom_2180, 100) limit 10
    ) temp1
    group by teryt_simc
    order by cnt desc
  ) temp2
  limit 1
) s on true
;
