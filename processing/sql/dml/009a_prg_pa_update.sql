-- dodaj ulic jeżeli simc pasuje i nazwy ulicy się mniej więcej pokrywają
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
    and prg.pa.teryt_simc is not null
    and prg.pa.ul is not null and prg.pa.teryt_ulic is null
    and u1.sym = prg.pa.teryt_simc
    and (
        trim(concat((u1.nazwa_2 || ' '), u1.nazwa_1)) ilike '%' || prg.pa.ul || '%'
        or
        prg.pa.ul ilike  '%' || trim(concat((u1.nazwa_2 || ' '), u1.nazwa_1)) || '%'
        or
        u1.nazwa_1 ilike  '%' || prg.pa.ul || '%'
        or
        prg.pa.ul ilike  '%' || u1.nazwa_1 || '%'
    )
    and u1.cecha = cm.cecha
    and exists (
        select 1
        from prg.pa, teryt.ulic u1
        where 1=1
            and prg.pa.teryt_simc is not null
            and prg.pa.ul is not null and prg.pa.teryt_ulic is null
            and u1.sym = prg.pa.teryt_simc
            and (
                trim(concat((u1.nazwa_2 || ' '), u1.nazwa_1)) ilike '%' || prg.pa.ul || '%'
                or
                prg.pa.ul ilike  '%' || trim(concat((u1.nazwa_2 || ' '), u1.nazwa_1)) || '%'
                or
                u1.nazwa_1 ilike  '%' || prg.pa.ul || '%'
                or
                prg.pa.ul ilike  '%' || u1.nazwa_1 || '%'
            )
    )
;
