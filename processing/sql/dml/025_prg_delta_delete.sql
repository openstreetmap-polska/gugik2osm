-- set jit=on;

-- delete from prg.delta_new prg
-- where exists(
--     select 1
--     from osm_hashed osm
--     where st_dwithin(prg.geom, osm.geom, 2)
-- );
-- analyze prg.delta_new;
