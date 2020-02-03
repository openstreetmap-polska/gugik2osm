insert into prg.pa_hashed
select
    md5(concat(lower(prg.teryt_msc), coalesce(lower(prg.teryt_ulica), ''), prg.nr)),
    lokalnyid,
    gml geom
from prg.pa prg
join teryt.simc on prg.teryt_simc = simc.sym
where
    gml && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
    and prg.teryt_msc is not null
    and not (prg.teryt_ulic is null and prg.ul is not null)
    and not (simc.rm like '9%' and prg.teryt_ulica is null)
;