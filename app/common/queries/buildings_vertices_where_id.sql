select
    way_id,
    array_agg(ARRAY[cast(st_x((dp).geom) as numeric(10, 8)), cast(st_y((dp).geom) as numeric(10, 8))]) as arr
from (
    select row_number() over() * -1 - 100000 as way_id, ST_DumpPoints(geom) dp
    from prg.lod1_buildings
    left join exclude_lod1 using(id)
    where id in %s
        and exclude_lod1.id is null
    limit 50000
) a
group by way_id;
