-- dodaj simc po terc6 i nazwie msc (kolejność słów bez znaczenia)
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
    and prg.pa.terc6 = s1.woj || s1.pow || s1.gmi
    and strings_equivalent(lower(prg.pa.msc), lower(s1.nazwa))
    and exists(
        select 1
        from prg.pa, teryt.simc s1
        where
            prg.pa.teryt_simc is null
            and prg.pa.terc6 = s1.woj || s1.pow || s1.gmi
            and strings_equivalent(lower(prg.pa.msc), lower(s1.nazwa))
    )
;
analyze prg.pa;
