delete from prg.delta_new
using (
    SELECT prg.lokalnyid
    FROM prg.delta_new prg
    JOIN osm_addr_polygon osm
        ON (st_intersects(prg.geom, st_transform(osm.geometry, 2180)) AND (osm.name = prg.nr_standaryzowany)) -- name = nr
) dd
where delta_new.lokalnyid = dd.lokalnyid;
analyze prg.delta_new;
