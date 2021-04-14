drop table if exists addresses;

select
        prg.lokalnyid,
        prg.teryt_msc,
        prg.teryt_simc,
        coalesce(prg.osm_ulica, prg.teryt_ulica, '') teryt_ulica,
        prg.teryt_ulic,
        prg.numerporzadkowy nr,
        prg.pna,
        prg.nr nr_standaryzowany,
        prg.gml geom_2180
into addresses
from prg.pa prg
join teryt.simc on prg.teryt_simc = simc.sym
where
    prg.teryt_msc is not null
    and not (prg.teryt_ulic is null and prg.ul is not null)
    and not (simc.rm like '9%' and prg.teryt_ulica is null);

create index if not exists addresses_geom on addresses using gist (geom_2180);
cluster addresses using addresses_geom;
create index if not exists addresses_lokalnyid on addresses using btree (lokalnyid);
analyze addresses;
