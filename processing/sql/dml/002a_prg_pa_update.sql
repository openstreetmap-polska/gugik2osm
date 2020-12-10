-- dodaj simc i ulic jeżeli zgadzają się z teryt - WARSZAWA
update prg.pa
set (
    teryt_msc,
    teryt_simc,
    teryt_ulica,
    teryt_ulic
) = (
    s1.nazwa,
    case
      when substring(prg.pa.terc6, 1, 4) in ('0264', '1061', '1261', '1465', '3064') then prg.pa.simc
      else s1.sym
    end,
    trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)),
    u1.sym_ul
)
from teryt.simc s1, teryt.ulic u1, teryt.cecha_mapping cm
where 1=1
    and prg.pa.simc is not null and prg.pa.teryt_simc is null
    and prg.pa.ulic is not null and prg.pa.teryt_ulic is null
    and substring(prg.pa.terc6, 1, 4) = '1465'
    and s1.woj = '14' and s1.pow = '65'
    and prg.pa.ulic = u1.sym_ul and u1.sym = s1.sym
    and u1.cecha = cm.cecha
;
