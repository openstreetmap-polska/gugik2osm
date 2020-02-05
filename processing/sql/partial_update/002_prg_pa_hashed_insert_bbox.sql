insert into prg.pa_hashed
select
    md5(concat(lower(prg.teryt_msc), coalesce(lower(prg.teryt_ulica), ''), prg.nr)),
    lokalnyid,
    gml geom
from prg.pa prg
join teryt.simc on prg.teryt_simc = simc.sym
where
    -- make sure given bounding box is valid
    ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857)
    and
    gml && ST_Transform(ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, 3857), 2180)
    and prg.teryt_msc is not null
    and not (prg.teryt_ulic is null and prg.ul is not null)
    and not (simc.rm like '9%%' and prg.teryt_ulica is null)
;