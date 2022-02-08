set jit=on;

drop table if exists prng_new;
create table prng_new AS
SELECT
    prng.id,
    prng.geom,
    liczba_adresow,
    liczba_budynkow,
    liczba_adresow+liczba_budynkow as count
FROM stg_prng_miejscowosci prng
LEFT JOIN lateral (
    select count(*) liczba_adresow
    from prg.delta a
    left join exclude_prg ep on a.lokalnyid=ep.id
    where 1=1
        and st_dwithin(st_transform(prng.geom, 2180), a.geom, 1000)
        and ep.id is null
) adr on true
LEFT JOIN lateral (
    select count(*) liczba_budynkow
    from bdot_buildings b
    left join exclude_bdot_buildings ebb on b.lokalnyid=ebb.id
    where 1=1
        and st_dwithin(prng.geom, b.geom_4326, 0.01)
        and ebb.id is null
) bud on true
;
