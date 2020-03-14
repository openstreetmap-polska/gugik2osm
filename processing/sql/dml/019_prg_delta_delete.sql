delete from prg.delta_new prg
using osm_adr osm
where st_dwithin(prg.geom, st_transform(osm.geom, 2180), 50) and prg.nr = osm.nr ;
analyze prg.delta_new;
