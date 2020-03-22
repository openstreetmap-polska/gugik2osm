COPY (
    select
        lokalnyid,
        woj.nazwa wojewodztwo,
        pow.nazwa powiat,
        terc.woj || terc.pow || terc.gmi || terc.rodz kod_gminy,
        terc.nazwa gmina,
        teryt_simc kod_miejscowosci,
        teryt_msc miejscowosc,
        teryt_ulic kod_ulicy,
        teryt_ulica ulica,
        nr,
        pna,
        st_x(gml) x_2180,
        st_y(gml) y_2180,
        st_x(st_transform(gml, 4326)) x_4326,
        st_y(st_transform(gml, 4326)) y_4326
    from prg.pa prg
    join teryt.simc on prg.teryt_simc = simc.sym
    join teryt.terc on simc.woj=terc.woj and simc.pow=terc.pow and simc.gmi=terc.gmi and simc.rodz_gmi=terc.rodz
    join teryt.terc pow on simc.woj=pow.woj and simc.pow=pow.pow and pow.gmi is null
    join teryt.terc woj on simc.woj=woj.woj and woj.pow is null
    where
        prg.teryt_msc is not null
        and not (prg.teryt_ulic is null and prg.ul is not null)
        and not (simc.rm like '9%' and prg.teryt_ulica is null)
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
