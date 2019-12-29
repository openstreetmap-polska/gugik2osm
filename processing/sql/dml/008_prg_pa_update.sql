-- test: dodaj ulic jeżeli kod powiatu i nazwa ul się zgadza dla 5 miast/powiatów z delegaturami
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
    and substring(prg.pa.terc6, 1, 4) in ('1465', '3064', '0264', '1261', '1061')
    and prg.pa.ul is not null and prg.pa.teryt_ulic is null
    and u1.sym = s1.sym
    and substring(prg.pa.terc6, 1, 4) = s1.woj || s1.pow
    and (
        trim(lower(concat((u1.nazwa_2 || ' '), u1.nazwa_1))) = lower(prg.pa.ul)
        or
        lower(u1.nazwa_1) = lower(prg.pa.ul)
    )
    and u1.cecha = cm.cecha
--     and exists (
--         select 1
--         from teryt.ulic u1, teryt.simc s1
--         where 1=1
--             and substring(prg.pa.terc6, 1, 4) in ('1465', '3064', '0264', '1261', '1061')
--             and prg.pa.ul is not null and prg.pa.teryt_ulic is null
--             and u1.sym = s1.sym
--             and substring(prg.pa.terc6, 1, 4) = s1.woj || s1.pow
--             and (
--                 trim(lower(concat((u1.nazwa_2 || ' '), u1.nazwa_1))) = lower(prg.pa.ul)
--                 or
--                 lower(u1.nazwa_1) = lower(prg.pa.ul)
--             )
--     )
;
