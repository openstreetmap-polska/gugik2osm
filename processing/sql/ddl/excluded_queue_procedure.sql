create or replace procedure process_excluded_queue ()
language plpgsql
as $$
declare
    temp_count integer := 0;
begin

    -- prepare temp tables
    create temporary table prg_ids (id uuid);
    create temporary table b_ids (id uuid);
    create temporary table tiles_to_update (z int, x int, y int);

    -- prg_ids
    insert into prg_ids
        select id
        from exclude_prg_queue
        where processed = false
    ;
    select count(*) into temp_count from prg_ids ;
    raise notice 'Reported PRG addresses to process: % .', temp_count ;

    -- b_ids
    insert into b_ids
        select id
        from exclude_bdot_buildings_queue
        where processed = false
    ;
    select count(*) into temp_count from b_ids ;
    raise notice 'Reported BDOT buildings to process: % .', temp_count ;

    -- update tiles
    insert into tiles_to_update
        select z, x, y
        from prg_ids prg
        join prg.delta d on d.lokalnyid = prg.id
        join tiles t on z >= 8 and t.bbox && st_transform(d.geom, 3857)
    ;
    insert into tiles_to_update
        select z, x, y
        from b_ids
        join bdot_buildings b on b.lokalnyid = b_ids.id
        join tiles t on z >= 8 and t.bbox && st_transform(b.geom_4326, 3857)
    ;
    with
    u as (
        update tiles t
        set mvt = mvt(t.z, t.x, t.y)
        from (select distinct z, x, y from tiles_to_update) u
        where 1=1
            and t.z = u.z
            and t.x = u.x
            and t.y = u.y
        returning 1
    )
    select count(*) into temp_count from u ;
    raise notice 'tiles UPDATE: % .', temp_count ;

    -- move ids
    insert into exclude_prg (id)
        select id
        from prg_ids
    on conflict do nothing
    ;
    insert into exclude_bdot_buildings (id)
        select id
        from b_ids
    on conflict do nothing
    ;
    delete from exclude_prg_queue
    using prg_ids
    where prg_ids.id = exclude_prg_queue.id
    ;
    delete from exclude_bdot_buildings_queue
    using b_ids
    where b_ids.id = exclude_bdot_buildings_queue.id
    ;


    drop table if exists prg_ids;
    drop table if exists b_ids;
    drop table if exists tiles_to_update;

    commit;

end;
$$
;
