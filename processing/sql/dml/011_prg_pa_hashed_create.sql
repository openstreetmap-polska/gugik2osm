drop table if exists prg.pa_hashed;
create table prg.pa_hashed as
select
    md5(concat(lower(prg.teryt_msc), coalesce(lower(prg.teryt_ulica), ''), prg.nr)) hash,
    lokalnyid,
    gml geom
from prg.pa prg
join teryt.simc on prg.teryt_simc = simc.sym
where
    prg.teryt_msc is not null
    and not (prg.teryt_ulic is null and prg.ul is not null)
    and not (simc.rm like '9%' and prg.teryt_ulica is null)
;
