CREATE OR REPLACE VIEW bdot.v_bubd_a as
    SELECT
        powiat,
        lokalnyid::uuid,
        cast(wersjaid as timestamp) wersjaid,
        status_bdot,
        nazwa,
        kategoria_bdot,
        funkcja_ogolna_budynku,
        concat(
            fs0.funkcja_szczegolowa_budynku,
            ', ' || fs1.funkcja_szczegolowa_budynku,
            ', ' || fs2.funkcja_szczegolowa_budynku,
            ', ' || fs3.funkcja_szczegolowa_budynku,
            ', ' || fs4.funkcja_szczegolowa_budynku,
            ', ' || fs5.funkcja_szczegolowa_budynku,
            ', ' || fs6.funkcja_szczegolowa_budynku,
            ', ' || fs7.funkcja_szczegolowa_budynku,
            ', ' || fs8.funkcja_szczegolowa_budynku,
            ', ' || fs9.funkcja_szczegolowa_budynku,
            ', ' || fs10.funkcja_szczegolowa_budynku
        ) funkcja_szczegolowa_budynku,
        cast(liczbakondygnacji as smallint) liczba_kondygnacji,
        zabytek,
        x_skrkarto skrot_karto,
        cast(x_aktualnoscg as date) aktualnosc_geometrii,
        cast(x_aktualnosca as date) aktualnosc_atrybutow,
        cast(koniecwersjiobiektu as timestamp) koniecwersjiobiektu,
        kodkst kod_kst,
        ST_GeomFromGML((xpath('/geometry/*', geometry::xml))[1]::text) geom_a_2180
    FROM bdot.stg_budynki_ogolne_poligony b
    LEFT JOIN bdot.lookup_x_kod using (x_kod)
    LEFT JOIN bdot.lookup_x_katistnienia using (x_katIstnienia)
    LEFT JOIN bdot.lookup_funogolnabudynku using (funOgolnaBudynku)
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs0 on fs0.funSzczegolowaBudynku=b.funSzczegolowaBudynku
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs1 on fs1.funSzczegolowaBudynku=b.funszczegolowabudynku_01
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs2 on fs2.funSzczegolowaBudynku=b.funszczegolowabudynku_02
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs3 on fs3.funSzczegolowaBudynku=b.funszczegolowabudynku_03
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs4 on fs4.funSzczegolowaBudynku=b.funszczegolowabudynku_04
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs5 on fs5.funSzczegolowaBudynku=b.funszczegolowabudynku_05
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs6 on fs6.funSzczegolowaBudynku=b.funszczegolowabudynku_06
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs7 on fs7.funSzczegolowaBudynku=b.funszczegolowabudynku_07
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs8 on fs8.funSzczegolowaBudynku=b.funszczegolowabudynku_08
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs9 on fs9.funSzczegolowaBudynku=b.funszczegolowabudynku_09
    LEFT JOIN bdot.lookup_funszczegolowabudynku fs10 on fs10.funSzczegolowaBudynku=b.funszczegolowabudynku_10
    WHERE 1=1
        and lokalnyid ~ E'^[[:xdigit:]]{8}-([[:xdigit:]]{4}-){3}[[:xdigit:]]{12}$' -- check if uuid is valid
        and is_parsable_gml((xpath('/geometry/*', geometry::xml))[1]::text) -- check if geometry is valid
;
