drop table if exists prng_new;
create table prng_new AS
SELECT
    prng.id,
    prng.geom,
    liczba_adresow+liczba_budynkow as count
FROM stg_prng_miejscowosci prng
CROSS JOIN lateral (select count(*) liczba_adresow from prg.delta a where st_dwithin(st_transform(prng.geom, 2180), a.geom, 1000)) adr
CROSS JOIN lateral (select count(*) liczba_budynkow from prg.lod1_buildings b where st_dwithin(prng.geom, b.geom, 0.01)) bud
;
