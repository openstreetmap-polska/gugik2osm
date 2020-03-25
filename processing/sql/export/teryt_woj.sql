COPY (
    select
        woj as kod_woj,
        initcap(nazwa) wojewodztwo,
        nazdod,
        stan_na
    from teryt.terc
    where pow is null
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
