set jit=on;

drop table if exists prg.delta_new;
create unlogged table prg.delta_new as
    select
        pa.lokalnyid,
        pa.teryt_msc,
        pa.teryt_simc,
        coalesce(pa.osm_ulica, pa.teryt_ulica) teryt_ulica,
        pa.teryt_ulic,
        pa.numerporzadkowy nr,
        pa.pna,
        pa.gml geom,
        pa.nr nr_standaryzowany
    from prg.pa_hashed prg
    join prg.pa using (lokalnyid)
    left join osm_hashed osm
        on (prg.hash = osm.hash and st_dwithin(prg.geom, osm.geom, 150))
    where 1=1
        and osm.hash is null
        and pa.status in ('istniejacy', 'wTrakcieBudowy')
        and pa.numerporzadkowy not like '%,%'
        and pa.numerporzadkowy not ilike '% do %'
        and pa.numerporzadkowy !~ '^\d+([ ]+\d+)+$'
        and pa.numerporzadkowy !~ '^B\.*N\.*.*$'
        and pa.numerporzadkowy !~ '^[\.0 \-]+$'
;
create index if not exists delta_gis_new on prg.delta_new using gist (geom);
cluster prg.delta_new using delta_gis_new;
create index if not exists delta_lokalnyid_new on prg.delta_new using btree (lokalnyid);
analyze prg.delta_new;
