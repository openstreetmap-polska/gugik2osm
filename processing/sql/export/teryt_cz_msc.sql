COPY (
    with
    czg as (
        select
            woj || pow || gmi || rodz as kod_cz_gmi,
            nazdod rodz_cz_gmi
        from teryt.terc
        where rodz not in ('1', '2', '3')
    ),
    m as (
        select
            g.*,
            czg.*,
            rm kod_rodz_msc,
            nazwa_rm rodzaj_msc,
            sym kod_msc,
            nazwa miejscowosc
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
    ),
    dzielnice as (
        select
    --        a.woj kod_woj,
    --        a.woj || a.pow kod_pow,
    --        a.woj || a.pow || b.gmi || b.rodz_gmi kod_gmi,
            a.woj || a.pow || a.gmi || a.rodz_gmi kod_cz_gmi,
            a.rm kod_rodz_cz_msc,
            nazwa_rm rodzaj_cz_msc,
            a.nazwa czesc_miejscowosci,
            a.sym kod_cz_msc,
            b.sym kod_msc,
            a.stan_na
        from (
            select
                woj,
                pow,
                gmi,
                rodz_gmi,
                rm,
                case
                  when woj = '14' then nazwa
                  else substring(nazwa, position('-' in nazwa) + 1)
                end nazwa,
                sym,
                sympod,
                simc.stan_na
            from teryt.simc
            where (woj, pow) in (('02', '64'), ('10', '61'), ('12', '61'), ('14', '65'), ('30', '64')) and rodz_gmi <> '1'
        ) a
        join (
            select woj, pow, gmi, rodz_gmi, sym from teryt.simc where simc.sym = simc.sympod
        ) b on a.woj=b.woj and a.pow=b.pow and b.gmi='01' and b.rodz_gmi='1'
        join teryt.wmrodz using(rm)
    ),
    result as (
        select
            m.kod_woj,
            m.wojewodztwo,
            m.kod_pow,
            m.powiat,
            m.kod_gmi,
            m.gmina,
            m.rodz_gminy,
            czg.kod_cz_gmi,
            czg.rodz_cz_gmi,
            m.kod_rodz_msc,
            m.rodzaj_msc,
            m.kod_msc,
            m.miejscowosc,
            dzielnice.kod_rodz_cz_msc,
            dzielnice.rodzaj_cz_msc,
            dzielnice.kod_cz_msc,
            dzielnice.czesc_miejscowosci,
            dzielnice.stan_na
        from dzielnice
        join m using(kod_msc)
        join czg on dzielnice.kod_cz_gmi=czg.kod_cz_gmi

        union all

        select
            m.*,
            rm kod_rodz_cz_msc,
            nazwa_rm rodzaj_cz_msc,
            sym kod_cz_msc,
            nazwa czesc_miejscowosci,
            simc.stan_na
        from teryt.simc
        join teryt.wmrodz using (rm)
        join m on simc.sympod = m.kod_msc
        where
            simc.sym <> simc.sympod
            and
            (woj, pow) not in (('02', '64'), ('10', '61'), ('12', '61'), ('14', '65'), ('30', '64'))
    )
    select * from result
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
