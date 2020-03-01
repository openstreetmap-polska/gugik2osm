drop table if exists prng;
create unlogged table prng AS
SELECT
    prng.id,
    prng.geom,
    liczba_adresow+liczba_budynkow as count
FROM stg_prng_miejscowosci prng
CROSS JOIN lateral (select count(*) liczba_adresow from prg.delta a where st_dwithin(st_transform(prng.geom, 2180), a.geom, 1000)) adr
CROSS JOIN lateral (select count(*) liczba_budynkow from prg.lod1_buildings b where st_dwithin(prng.geom, b.geom, 0.01)) bud
;

create index idx_prng_geom on prng using gist (geom);
cluster prng using idx_prng_geom;
create index idx_prng_count on prng using btree (count desc);
--create index idx_prng_id on prng using btree (id);
alter table prng set logged;
