create unlogged table prng_new AS
SELECT
    prng.id,
    prng.geom,
    liczba_adresow+liczba_budynkow as count
FROM stg_prng_miejscowosci prng
CROSS JOIN lateral (select count(*) liczba_adresow from prg.delta a where st_dwithin(st_transform(prng.geom, 2180), a.geom, 1000)) adr
CROSS JOIN lateral (select count(*) liczba_budynkow from prg.lod1_buildings b where st_dwithin(prng.geom, b.geom, 0.01)) bud
;

create index idx_prng_geom_new on prng using gist (geom);
cluster prng using idx_prng_geom_new;
create index idx_prng_count_new on prng using btree (count desc);
--create index idx_prng_id on prng using btree (id);
alter table prng_new set logged;

alter table prng rename to prng_old;
alter table prng_new rename to prng;
drop table prng_old;
alter index idx_prng_geom_new rename to idx_prng_geom;
alter index idx_prng_count_new rename to idx_prng_count;

analyze prng;
