-- dodaj simc i ulic jeżeli zgadzają się z teryt i nazwa msc ok
update prg.pa
set (
    teryt_msc,
    teryt_simc,
    teryt_ulica,
    teryt_ulic
) = (
    s1.nazwa,
    s1.sym,
    trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)),
    u1.sym_ul
)
from teryt.simc s1, teryt.ulic u1, teryt.cecha_mapping cm
where 1=1
    and prg.pa.simc is not null and prg.pa.teryt_simc is null
    and prg.pa.ulic is not null and prg.pa.teryt_ulic is null
    and prg.pa.simc = s1.sym
    and prg.pa.ulic = u1.sym_ul and u1.sym = prg.pa.simc
    and u1.cecha = cm.cecha
    and not (
        replace(lower(s1.nazwa), '-', ' ') <> replace(lower(prg.pa.msc), '-', ' ')
        and not (prg.pa.msc ilike '%' || s1.nazwa or prg.pa.msc ilike s1.nazwa || '%')
    )
;
