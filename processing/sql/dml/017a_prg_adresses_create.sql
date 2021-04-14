drop table if exists adresses;

select
        prg.lokalnyid,
        prg.teryt_msc,
        prg.teryt_simc,
        coalesce(prg.osm_ulica, prg.teryt_ulica, '') teryt_ulica,
        prg.teryt_ulic,
        prg.numerporzadkowy nr,
        prg.pna,
        prg.nr nr_standaryzowany,
        prg.gml geom
into adresses
from prg.pa prg
join teryt.simc on prg.teryt_simc = simc.sym
left join exclude_prg e on lokalnyid = e.id
where
    prg.teryt_msc is not null
    and not (prg.teryt_ulic is null and prg.ul is not null)
    and not (simc.rm like '9%' and prg.teryt_ulica is null);

create index if not exists adresses_geom on adresses using gist (geom);
cluster adresses using adresses_geom;
create index if not exists adresses_lokalnyid on adresses using btree (lokalnyid);
analyze adresses;
