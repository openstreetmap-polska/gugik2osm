alter table prng rename to prng_old;
alter table prng_new rename to prng;
alter index idx_prng_geom rename to idx_prng_geom_old;
alter index idx_prng_count rename to idx_prng_count_old;
alter index idx_prng_geom_new rename to idx_prng_geom;
alter index idx_prng_count_new rename to idx_prng_count;
