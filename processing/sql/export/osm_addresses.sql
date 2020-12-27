COPY (
    with
    tab as (
        select osm_id, miejscowosc, cz_msc, ulica, type as nr_porzadkowy, kod_pna, kod_ulic, kod_simc, ST_Centroid(geometry) geom
        from osm_addr_polygon
        union all
        select osm_id, miejscowosc, cz_msc, ulica, type as nr_porzadkowy, kod_pna, kod_ulic, kod_simc, geometry
        from osm_addr_point
    ),
    a as (
        select
          osm_id,
          case when miejscowosc = '' then null else trim(miejscowosc) end msc,
          case when cz_msc = '' then null else trim(cz_msc) end czmsc,
          case when ulica = '' then null else trim(ulica) end ul,
          upper(trim(nr_porzadkowy)) nr,
          case when kod_pna ~ '^\d{2}-\d{3}$' and kod_pna <> '00-000' then kod_pna else null end pna,
          case when kod_ulic ~ '^\d{5}$' then kod_ulic else null end ulic,
          case when kod_simc ~ '^\d{7}$' then kod_simc else null end simc,
          geom
        from tab
    )
    SELECT
        osm_id,
        msc miejscowosc,
        czmsc czesc_miejscowosci,
        ul ulica,
        nr,
        pna,
        ulic kod_ulic,
        simc kod_miejscowosci,
        st_x(geom) x_4326,
        st_y(geom) y_4326
    FROM a
    where
    -- removed this condition as some addresses don't have neither addr:city nor addr:place tags
    --  coalesce(msc, czmsc) is not null
    --  and
        nr is not null
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
