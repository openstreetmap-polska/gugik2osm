COPY (
    select
        p.*,
        woj || pow || gmi || rodz as kod_gmi,
        initcap(nazwa) gmina,
        nazdod,
        stan_na
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
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
