COPY (
    select woj, pow, gmi, teryt_simc, teryt_msc, teryt_ulic, teryt_ulica
    from prg.pa
    where osm_ulica is null and lower(teryt_ulica) like '%.%'
    group by woj, pow, gmi, teryt_simc, teryt_msc, teryt_ulic, teryt_ulica
    order by teryt_ulica, teryt_msc
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
