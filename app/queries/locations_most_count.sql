select st_x(geom) longitude, st_y(geom) latitude from prng order by count desc limit 1000;
