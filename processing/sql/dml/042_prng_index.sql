create index idx_prng_geom_new on prng_new using gist (geom);
cluster prng_new using idx_prng_geom_new;
create index idx_prng_count_new on prng_new using btree (count desc);
analyze prng_new;
