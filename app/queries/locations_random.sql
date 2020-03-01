-- efficient sampling
-- https://www.postgresql.org/docs/current/sql-select.html#SQL-FROM
-- get around 1k rows from table that has around 100k rows (1%)
SELECT st_x(geom) longitude, st_y(geom) latitude FROM prng TABLESAMPLE BERNOULLI ((1000 * 100) / 100000.0) ;
