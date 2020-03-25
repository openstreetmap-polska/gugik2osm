COPY (
    select
        g.*,
        czg.*,
        rm kod_rodz_msc,
        nazwa_rm rodzaj_msc,
        sym kod_msc,
        nazwa miejscowosc,
        simc.stan_na
    from teryt.simc
    join teryt.wmrodz using (rm)
    join (
        select
            p.*,
            woj || pow || gmi || rodz as kod_gmi,
            initcap(nazwa) gmina,
            nazdod rodz_gminy
        from teryt.terc
        join (
            select
                w.kod_woj,
                w.wojewodztwo,
                woj || pow as kod_pow,
                initcap(nazwa) powiat
            from teryt.terc
            join (
                select
                    woj as kod_woj,
                    initcap(nazwa) wojewodztwo
                from teryt.terc
                where pow is null
            ) w on w.kod_woj = terc.woj
            where pow is not null and gmi is null
        ) p on woj || pow = p.kod_pow
        where gmi is not null and rodz in ('1', '2', '3')
    ) g on  woj || pow || gmi = substring(kod_gmi, 1, 6)
    left join (
        select
            woj || pow || gmi || rodz as kod_cz_gmi,
            nazdod rodz_cz_gmi
        from teryt.terc
        where rodz not in ('1', '2', '3')
    ) czg on woj || pow || gmi || rodz_gmi = kod_cz_gmi
    where sym = sympod and nazwa_rm not in ('delegatura', 'dzielnica')
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
