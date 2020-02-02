-- dodaj ulic jeżeli simc pasuje i nazwa ulicy się zgadza
update prg.pa
set (
    teryt_ulica,
    teryt_ulic
) = (
    trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)),
    u1.sym_ul
)
from teryt.ulic u1, teryt.cecha_mapping cm
where 1=1
    and prg.pa.teryt_simc is not null
    and prg.pa.ul is not null and prg.pa.teryt_ulic is null
    and u1.sym = prg.pa.teryt_simc
    and (
        trim(lower(concat((u1.nazwa_2 || ' '), u1.nazwa_1))) = lower(prg.pa.ul)
        or
        lower(u1.nazwa_1) = lower(prg.pa.ul)
    )
    and u1.cecha = cm.cecha
    and exists (
        select 1
        from prg.pa, teryt.ulic u1, teryt.cecha_mapping cm
        where 1=1
            and prg.pa.teryt_simc is not null
            and prg.pa.ul is not null and prg.pa.teryt_ulic is null
            and u1.sym = prg.pa.teryt_simc
            and (
                trim(lower(concat((u1.nazwa_2 || ' '), u1.nazwa_1))) = lower(prg.pa.ul)
                or
                lower(u1.nazwa_1) = lower(prg.pa.ul)
            )
            and u1.cecha = cm.cecha
    )
;
