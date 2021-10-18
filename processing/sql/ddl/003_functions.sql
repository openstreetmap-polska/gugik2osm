CREATE or replace FUNCTION is_parsable_gml(text) RETURNS boolean
    LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE
    AS $_$
declare
    temp geometry;
begin
    temp = st_geomfromgml($1);
    return true;
exception
    when others then
        return false;
end;
$_$;

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

-- https://dba.stackexchange.com/questions/175368/compare-words-in-a-string-without-considering-their-positions
create or replace function strings_equivalent(a text, b text)
returns boolean as $$
select
  case
    when length(a) >= length(b) then (
      select count( exa1 ) from (
        select unnest( string_to_array( a, ' ' ) )
        except all
        select unnest( string_to_array( b, ' ' ) ) ) exa1
      ) = 0
    when length(a) < length(b) then (
      select count( exa2 ) from (
        select unnest( string_to_array( b, ' ' ) )
        except all
        select unnest( string_to_array( a, ' ' ) ) ) exa2
      ) = 0
    else false
  end
$$ language sql immutable;

create or replace procedure partial_update ()
language plpgsql
as $$
declare
    temp_count integer := 0;
begin

    -- prepare temp tables
    create temporary table exp (file_name text, z int, x int, y int);
    create temporary table exp_bounds (geom geometry(Polygon, 3857));
    create temporary table tiles_to_update (z int, x int, y int);

    -- select tiles that we need to process
    insert into exp
        select file_name, z, x, y
        from expired_tiles
        where processed = false
        limit 100000
    ;

    select count(*) into temp_count from exp ;
    raise notice 'Expired tiles to process: % .', temp_count ;

    -- create geometries of tiles
    insert into exp_bounds
    select ST_TileEnvelope(z, x, y) as geom
    from (
        select distinct z, x, y
        from exp
    ) t ;

    select count(*) into temp_count from exp_bounds ;
    raise notice 'Created: % geometries.', temp_count ;

    -- osm_adr_delete
    with
    d as (
        delete from osm_adr
        using exp_bounds
        where
            -- make sure given bounding box is valid
            ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
            and
            osm_adr.geom && ST_Transform(exp_bounds.geom, 4326)
        returning 1
    )
    select count(*) into temp_count from d ;
    raise notice 'osm_adr DELETE: % .', temp_count ;

    -- osm_adr_insert
    with
    i as (
        insert into osm_adr
            SELECT a.*
            FROM (
                select
                    case when miejscowosc = '' then null else trim(miejscowosc) end msc,
                    case when cz_msc = '' then null else trim(cz_msc) end czmsc,
                    case when ulica = '' then null else trim(ulica) end ul,
                    nr_porzadkowy as nr,
                    case when kod_pna ~ '^\d{2}-\d{3}$' and kod_pna <> '00-000' then kod_pna else null end pna,
                    case when kod_ulic ~ '^\d{5}$' then kod_ulic else null end ulic,
                    case when kod_simc ~ '^\d{7}$' then kod_simc else null end simc,
                    geom
                from (
                    select
                        miejscowosc,
                        cz_msc,
                        ulica,
                        ltrim(rtrim(replace(replace(upper(trim(type)), '\', '/'), ' ', ''), './'), '.0/') as nr_porzadkowy,
                        kod_pna,
                        kod_ulic,
                        kod_simc,
                        ST_Centroid(geometry) geom
                    from osm_addr_polygon
                    join exp_bounds
                    on geometry && ST_Transform(exp_bounds.geom, 4326) and ST_Centroid(geometry) && ST_Transform(exp_bounds.geom, 4326)
                    where
                        -- make sure given bounding box is valid
                        ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom

                    union all

                    select
                        miejscowosc,
                        cz_msc,
                        ulica,
                        ltrim(rtrim(replace(replace(upper(trim(type)), '\', '/'), ' ', ''), './'), '.0/') as nr_porzadkowy,
                        kod_pna,
                        kod_ulic,
                        kod_simc,
                        geometry
                    from osm_addr_point
                    join exp_bounds on geometry && ST_Transform(exp_bounds.geom, 4326)
                    where
                        -- make sure given bounding box is valid
                        ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
                ) tab
            ) a
            where
                -- removed this condition as some addresses don't have neither addr:city nor addr:place tags
                --  coalesce(msc, czmsc) is not null
                --  and
                nr is not null
        returning 1
    )
    select count(*) into temp_count from i ;
    raise notice 'osm_adr INSERT: % .', temp_count ;

    -- osm_hashed_delete
    with
    d as (
        delete from osm_hashed
        using exp_bounds
        where
            -- make sure given bounding box is valid
            ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
            and
            osm_hashed.geom && ST_Transform(exp_bounds.geom, 2180)
        returning 1
    )
    select count(*) into temp_count from d ;
    raise notice 'osm_hashed DELETE: % .', temp_count ;

    -- osm_hashed_insert
    with
    i as (
        insert into osm_hashed
            select md5(concat(lower(msc), coalesce(lower(ul), ''), nr)) hash, st_transform(osm_adr.geom, 2180) geom
            from osm_adr
            join exp_bounds on osm_adr.geom && ST_Transform(exp_bounds.geom, 4326)
            where
                -- make sure given bounding box is valid
                ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom

            union all

            select md5(concat(lower(czmsc), coalesce(lower(ul), ''), nr)) hash, st_transform(osm_adr.geom, 2180) geom
            from osm_adr
            join exp_bounds on osm_adr.geom && ST_Transform(exp_bounds.geom, 4326)
            where
                -- make sure given bounding box is valid
                ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
                and
                czmsc is not null
        returning 1
    )
    select count(*) into temp_count from i ;
    raise notice 'osm_hashed INSERT: % .', temp_count ;

    -- prg_delta_delete
    with
    d as (
        delete from prg.delta d
        using exp_bounds
        where
            -- make sure given bounding box is valid
            ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
            and
            d.geom && ST_Transform(exp_bounds.geom, 2180)
            and (
                exists (
                    select 1
                    from prg.pa_hashed prg, osm_hashed osm
                    where
                        st_dwithin(prg.geom, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        st_dwithin(osm.geom, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        d.lokalnyid = prg.lokalnyid
                        and
                        prg.hash = osm.hash
                        and
                        st_dwithin(prg.geom, osm.geom, 150)
                )
                or
                exists (
                    select 1
                    from prg.pa_hashed prg, osm_hashed osm
                    where
                        st_dwithin(prg.geom, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        st_dwithin(osm.geom, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        d.lokalnyid = prg.lokalnyid
                        and
                        st_dwithin(prg.geom, osm.geom, 2)
                )
                or
                exists (
                    select 1
                    from osm_adr osm
                    where
                        st_dwithin(osm.geom, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        st_dwithin(d.geom, st_transform(osm.geom, 2180), 40) and d.nr_standaryzowany = osm.nr
                )
                or
                exists (
                    select 1
                    from osm_addr_polygon osm
                    where
                        st_dwithin(osm.geometry, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        st_intersects(d.geom, st_transform(osm.geometry, 2180)) AND (osm.type = d.nr_standaryzowany) -- type = nr
                )
                or
                exists (
                    select 1
                    from osm_addr_polygon osm
                    where
                        st_dwithin(osm.geometry, ST_Transform(exp_bounds.geom, 2180), 150)
                        and
                        st_dwithin(d.geom, st_transform(osm.geometry, 2180), 15) AND (osm.type = d.nr_standaryzowany) -- type = nr
                )
            )
        returning 1
    )
    select count(*) into temp_count from d ;
    raise notice 'prg.delta DELETE: % .', temp_count ;

    -- bdot_buildings_delete
    with
    d as (
        delete from bdot_buildings b
        using osm_buildings o, exp_bounds
        where
            -- make sure given bounding box is valid
            ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
            and
            b.geom_4326 && ST_Transform(exp_bounds.geom, 4326)
            and
            o.geometry && ST_Transform(exp_bounds.geom, 4326)
            and
            st_intersects(b.geom_4326, o.geometry)
        returning 1
    )
    select count(*) into temp_count from d ;
    raise notice 'bdot_buildings DELETE: % .', temp_count ;

    -- bdot_buildings_delete 2
    with
    d as (
        delete from bdot_buildings b
        using osm_abandoned_or_demolished_buildings o, exp_bounds
        where
            -- make sure given bounding box is valid
            ST_Transform(ST_MakeEnvelope(14.0, 49.0, 24.03, 54.86, 4326), 3857) && exp_bounds.geom
            and
            b.geom_4326 && ST_Transform(exp_bounds.geom, 4326)
            and
            o.geometry && ST_Transform(exp_bounds.geom, 4326)
            and
            st_intersects(b.geom_4326, o.geometry)
        returning 1
    )
    select count(*) into temp_count from d ;
    raise notice 'bdot_buildings DELETE: % .', temp_count ;

    -- tiles_to_update
    insert into tiles_to_update
        select distinct z, x, y
        from tiles_bounds
        join exp_bounds on tiles_bounds.geom_3857 && exp_bounds.geom
        where z >= 8
    ;

    -- update tiles
    with
    u as (
        update tiles
        set mvt = mvt(tiles.z, tiles.x, tiles.y)
        from tiles_to_update
        where 1=1
            and tiles_to_update.z = tiles.z
            and tiles_to_update.x = tiles.x
            and tiles_to_update.y = tiles.y
        returning 1
    )
    select count(*) into temp_count from u ;
    raise notice 'tiles UPDATE: % .', temp_count ;

    -- mark tiles as processed
    update expired_tiles
    set processed = true
    from exp
    where 1=1
        and exp.file_name = expired_tiles.file_name
        and exp.z = expired_tiles.z
        and exp.x = expired_tiles.x
        and exp.y = expired_tiles.y
    ;

    drop table if exists exp;
    drop table if exists exp_bounds;
    drop table if exists tiles_to_update;

    commit ;

end;
$$
;

CREATE OR REPLACE FUNCTION mvt_clustered (
    IN bbox geometry,
    IN max_distance_distance float8,
    IN min_points_per_cluster integer
) RETURNS bytea
AS  $$
    with
    a as (
        select
            d.geom
        from prg.delta d
        left join exclude_prg e on d.lokalnyid = e.id
        where 1=1
            and e.id is null
            and d.geom && ST_Transform(bbox, 2180)
        limit 500000
    ),
    a2 as (
        select
            ST_ClusterDBSCAN(geom, max_distance_distance, min_points_per_cluster) over() clid,
            ST_Transform(geom, 3857) geom_3857
        from a
    ),
    a3 as (
        select
            ST_GeometricMedian(st_union(geom_3857)) centroid,
            count(*) no_of_points
        from a2
        group by clid
    ),
    a4 as (
        select
           ST_AsMVTGeom(
             centroid,
             bbox::box2d
           ) geom,
           no_of_points
        from a3
    ),
    b as (
        select
            ST_Transform(ST_Centroid(geom_4326), 3857) geom_3857
        from bdot_buildings b
        left join exclude_bdot_buildings e on b.lokalnyid = e.id
        where 1=1
            and e.id is null
            and geom_4326 && ST_Transform(bbox, 4326)
        limit 500000
    ),
    b2 as (
        select
            ST_ClusterDBSCAN(geom_3857, max_distance_distance, min_points_per_cluster) over() clid,
            geom_3857
        from b
    ),
    b3 as (
        select
            ST_GeometricMedian(st_union(geom_3857)) centroid,
            count(*) no_of_points
        from b2
        group by clid
    ),
    b4 as (
        select
            ST_AsMVTGeom(
                centroid,
                bbox::box2d
            ) geom,
            no_of_points
        from b3
    )
    select string_agg(layer, null) mvt
    from (
        select ST_AsMVT(a4.*, 'addresses_clustered') as layer from a4
        union all
        select ST_AsMVT(b4.*, 'buildings_clustered') as layer from b4
    ) t
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt_unclustered_geom_only (IN bbox geometry) RETURNS bytea
AS  $$
    with
    a as (
        select
           ST_AsMVTGeom(
             ST_Transform(d.geom, 3857),
             bbox::box2d
           ) geom
        from prg.delta d
        left join exclude_prg on d.lokalnyid=exclude_prg.id
        where d.geom && ST_Transform(bbox, 2180)
            and exclude_prg.id is null
        limit 500000
    ),
    b as (
        select
            ST_AsMVTGeom(
                ST_Transform(ST_Centroid(geom_4326), 3857),
                bbox::box2d
            ) geom
        from bdot_buildings
        where geom_4326 && ST_Transform(bbox, 4326)
        limit 500000
    )
    select string_agg(layer, null) mvt
    from (
        select ST_AsMVT(a.*, 'addresses_geomonly') as layer from a
        union all
        select ST_AsMVT(b.*, 'buildings_centroids') as layer from b
    ) t
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt_unclustered_with_details (IN bbox geometry) RETURNS bytea
AS  $$
    with a as (
        select
           d.lokalnyid,
           d.teryt_msc,
           d.teryt_simc,
           d.teryt_ulica,
           d.teryt_ulic,
           d.nr,
           d.pna,
           ST_AsMVTGeom(
             ST_Transform(d.geom, 3857),
             bbox::box2d
           ) geom
        from prg.delta d
        left join exclude_prg on d.lokalnyid = exclude_prg.id
        where d.geom && ST_Transform(bbox, 2180)
            and exclude_prg.id is null
        limit 500000
    ),
    b as (
        select
            lokalnyid,
            ST_AsMVTGeom(ST_Transform(geom_4326, 3857), bbox::box2d) geom,
            status_bdot,
            kategoria_bdot,
            funkcja_ogolna_budynku,
            funkcja_szczegolowa_budynku,
            aktualnosc_geometrii,
            aktualnosc_atrybutow,
            building,
            amenity,
            man_made,
            leisure,
            historic,
            tourism,
            building_levels
        from bdot_buildings b
        left join exclude_bdot_buildings ex on b.lokalnyid=ex.id
        where geom_4326 && ST_Transform(bbox, 4326)
            and ex.id is null
        limit 500000
    )
    select string_agg(layer, null) mvt
    from (
        select ST_AsMVT(a.*, 'addresses') as layer from a
        union all
        select ST_AsMVT(b.*, 'buildings') as layer from b
    ) t
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt (IN z int, IN x int, IN y int) RETURNS bytea
AS $$
    DECLARE
        bbox geometry;
    BEGIN
        bbox := ST_TileEnvelope(z, x, y);

        if z = 6 then
            RETURN mvt_clustered(bbox, 1000, 1);
        elsif z = 7 then
            RETURN mvt_clustered(bbox, 1000, 1);
        elsif z = 8 then
            RETURN mvt_clustered(bbox, 1000, 1);
        elsif z = 9 then
            RETURN mvt_clustered(bbox, 500, 1);
        elsif z = 10 then
            RETURN mvt_clustered(bbox, 200, 1);
        elsif z = 11 then
            RETURN mvt_unclustered_geom_only(bbox);
        elsif z = 12 then
            RETURN mvt_unclustered_geom_only(bbox);
        elsif z >= 13 and z <= 23 then
            RETURN mvt_unclustered_with_details(bbox);
        else
            raise notice 'Zoom % outside valid range.', z;
            RETURN null;
        end if;
    END;
$$ LANGUAGE plpgsql STABLE ;
