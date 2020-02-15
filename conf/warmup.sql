select * from
(select count(*) osm_adr_count from osm_adr) a,
(select count(*) prg_pa_count from prg.pa) b,
(select count(*) prg_pa_hashed_count from prg.pa_hashed) c,
(select count(*) osm_hashed_count from osm_hashed) d,
(select count(*) prg_delta_count from prg.delta) e,
(select count(*) tiles_count from tiles) f
where 1=1;
