CREATE OR REPLACE FUNCTION mvt_6_7 (IN bbox geometry) RETURNS bytea
AS  $$
    with
    a as (
        select distinct teryt_simc
        from prg.delta d
        left join exclude_prg on d.lokalnyid=exclude_prg.id
        where d.geom && ST_Transform(bbox, 2180)
            and exclude_prg.id is null
    ),
    b as (
        select
            ST_AsMVTGeom(
                ST_Transform(ST_GeometricMedian(st_union(d.geom)), 3857),
                bbox::box2d
            ) geom
            , count(*) no_of_points
        from a
        join prg.delta d using(teryt_simc)
        join teryt.simc on teryt_simc = sym
        group by woj, pow, gmi, rodz_gmi
    )
    select
        ST_AsMVT(b.*, 'prg2load_geomonly') mvt
    from b
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt_8_9 (IN bbox geometry) RETURNS bytea
AS  $$
    with
    a as (
        select distinct teryt_simc
        from prg.delta d
        left join exclude_prg on d.lokalnyid=exclude_prg.id
        where d.geom && ST_Transform(bbox, 2180)
            and exclude_prg.id is null
    ),
    b as (
        select
            ST_AsMVTGeom(
                ST_Transform(ST_GeometricMedian(st_union(d.geom)), 3857),
                bbox::box2d
            ) geom
            , count(*) no_of_points
        from a
        join prg.delta d using(teryt_simc)
        group by teryt_simc
    )
    select
        ST_AsMVT(b.*, 'prg2load_geomonly') mvt
    from b
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt_10_11 (IN bbox geometry) RETURNS bytea
AS  $$
    with
    a as (
        select distinct teryt_simc, coalesce(teryt_ulic, '99999') teryt_ulic
        from prg.delta d
        left join exclude_prg on d.lokalnyid=exclude_prg.id
        where d.geom && ST_Transform(bbox, 2180)
            and exclude_prg.id is null
    ),
    b as (
        select
            ST_AsMVTGeom(
                ST_Transform(ST_GeometricMedian(st_union(d.geom)), 3857),
                bbox::box2d
            ) geom
            , count(*) no_of_points
        from a
        join prg.delta d on a.teryt_simc=d.teryt_simc and a.teryt_ulic=coalesce(d.teryt_ulic, '99999')
        group by a.teryt_simc, a.teryt_ulic
    )
    select
        ST_AsMVT(b.*, 'prg2load_geomonly') mvt
    from b
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt_12_12 (IN bbox geometry) RETURNS bytea
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
    )
    select
        ST_AsMVT(a.*, 'prg2load_geomonly') mvt
    from a
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt_13_23 (IN bbox geometry) RETURNS bytea
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
    select (select ST_AsMVT(a.*, 'prg2load') from a) || (select ST_AsMVT(b.*, 'buildings') from b) mvt
$$ LANGUAGE SQL STABLE ;

CREATE OR REPLACE FUNCTION mvt (IN z int, IN x int, IN y int) RETURNS bytea
AS $$
    DECLARE
        bbox geometry;
    BEGIN
        bbox := ST_TileEnvelope(z, x, y);

        if z >= 6 and z <= 7 then
            RETURN mvt_6_7(bbox);
        elsif z >= 8 and z <= 9 then
            RETURN mvt_8_9(bbox);
        elsif z >= 10 and z <= 11 then
            RETURN mvt_10_11(bbox);
        elsif z >= 12 and z <= 12 then
            RETURN mvt_12_12(bbox);
        elsif z >= 13 and z <= 23 then
            RETURN mvt_13_23(bbox);
        else
            raise notice 'Zoom % outside valid range.', z;
            RETURN null;
        end if;
    END;
$$ LANGUAGE plpgsql STABLE ;
