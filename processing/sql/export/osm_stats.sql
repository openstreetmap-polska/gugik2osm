COPY (
    select * from osm_stats
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
