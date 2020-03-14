-- dodaj ulic jeżeli kod powiatu inazwy msc i ul się zgadzają
update prg.pa
set (
    teryt_ulica,
    teryt_ulic
) = (
    trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)),
    u1.sym_ul
)
from teryt.ulic u1, teryt.cecha_mapping cm, teryt.simc s1
where 1=1
    and prg.pa.ul is not null and prg.pa.teryt_ulic is null
    and u1.sym = s1.sym
    and substring(prg.pa.terc6, 1, 4) = s1.woj || s1.pow
    and lower(prg.pa.msc) = lower(s1.nazwa)
    and (
        trim(lower(concat((u1.nazwa_2 || ' '), u1.nazwa_1))) = lower(prg.pa.ul)
        or
        lower(u1.nazwa_1) = lower(prg.pa.ul)
    )
    and u1.cecha = cm.cecha
    and exists (
        select 1
        from prg.pa, teryt.ulic u1, teryt.simc s1
        where 1=1
            and prg.pa.ul is not null and prg.pa.teryt_ulic is null
            and u1.sym = s1.sym
            and substring(prg.pa.terc6, 1, 4) = s1.woj || s1.pow
            and lower(prg.pa.msc) = lower(s1.nazwa)
            and (
                trim(lower(concat((u1.nazwa_2 || ' '), u1.nazwa_1))) = lower(prg.pa.ul)
                or
                lower(u1.nazwa_1) = lower(prg.pa.ul)
            )
    )
;
analyze prg.pa;
