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
