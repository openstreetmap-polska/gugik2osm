-- dodaj simc i ulic jeżeli zgadzają się z teryt - KRAKÓW
update prg.pa
set (
    teryt_msc,
    teryt_simc,
    teryt_ulica,
    teryt_ulic
) = (
    initcap(prg.pa.msc),
    prg.pa.simc,
    trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)),
    u1.sym_ul
)
from (
    select woj, pow, sym_ul, nazwa_1, nazwa_2, cecha
    from teryt.ulic
    group by woj, pow, sym_ul, nazwa_1, nazwa_2, cecha
) as u1, teryt.cecha_mapping cm
where 1=1
    and prg.pa.simc is not null and prg.pa.teryt_simc is null
    and prg.pa.ulic is not null and prg.pa.teryt_ulic is null
    and substring(prg.pa.terc6, 1, 4) = '1261'
    and u1.woj = '12' and u1.pow = '61'
    and prg.pa.ulic = u1.sym_ul
    and u1.cecha = cm.cecha
;
