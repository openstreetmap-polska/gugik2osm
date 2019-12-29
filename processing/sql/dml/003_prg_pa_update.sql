-- dodaj simc jeżeli kod zgadza się z teryt i nazwa msc ok
update prg.pa
set (
    teryt_msc,
    teryt_simc
) = (
    s1.nazwa,
    s1.sym
)
from teryt.simc s1
where
    prg.pa.teryt_simc is null
    and prg.pa.simc is not null
    and prg.pa.simc = s1.sym
    and not (
        replace(lower(s1.nazwa), '-', ' ') <> replace(lower(prg.pa.msc), '-', ' ')
        and not (prg.pa.msc ilike '%' || s1.nazwa or prg.pa.msc ilike s1.nazwa || '%')
    )
;
