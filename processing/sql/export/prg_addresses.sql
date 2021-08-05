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
        st_x(geom_2180) x_2180,
        st_y(geom_2180) y_2180,
        st_x(st_transform(geom_2180, 4326)) x_4326,
        st_y(st_transform(geom_2180, 4326)) y_4326,
        osm_street_name osm_ulica
    from addresses prg
    join teryt.simc on prg.teryt_simc = simc.sym
    join teryt.terc on simc.woj=terc.woj and simc.pow=terc.pow and simc.gmi=terc.gmi and simc.rodz_gmi=terc.rodz
    join teryt.terc pow on simc.woj=pow.woj and simc.pow=pow.pow and pow.gmi is null
    join teryt.terc woj on simc.woj=woj.woj and woj.pow is null
    left join street_names_mappings sm on teryt_simc_code=prg.teryt_simc and teryt_ulic_code=prg.teryt_ulic
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
