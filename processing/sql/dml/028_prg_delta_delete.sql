set jit=on;

delete from prg.delta_new prg
using (
    select prg.lokalnyid
    from prg.delta_new prg
    join (
        select teryt_simc, teryt_ulic, nr
        from prg.delta_new
        group by teryt_simc, teryt_ulic, nr
        having count(*) > 1
    ) dd using (teryt_simc, teryt_ulic, nr)
) ddd
where prg.lokalnyid = ddd.lokalnyid;
analyze prg.delta_new;
