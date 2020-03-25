COPY (
    select
        w.*,
        woj || pow as kod_pow,
        initcap(nazwa) powiat,
        nazdod,
        stan_na
    from teryt.terc
    join (
        select
            woj as kod_woj,
            initcap(nazwa) wojewodztwo
        from teryt.terc
        where pow is null
    ) w on w.kod_woj = terc.woj
    where pow is not null and gmi is null
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
