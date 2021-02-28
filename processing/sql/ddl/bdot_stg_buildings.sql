create unlogged table if not exists bdot.stg_budynki_ogolne_poligony (
    lokalnyid              text,
    wersjaid               text,
    x_kod                  text,
    x_skrkarto             text,
    x_katistnienia         text,
    x_aktualnoscg          text,
    x_aktualnosca          text,
    koniecwersjiobiektu    text,
    funogolnabudynku       text,
    funszczegolowabudynku  text,
    funszczegolowabudynku_01  text,
    funszczegolowabudynku_02  text,
    funszczegolowabudynku_03  text,
    funszczegolowabudynku_04  text,
    funszczegolowabudynku_05  text,
    funszczegolowabudynku_06  text,
    funszczegolowabudynku_07  text,
    funszczegolowabudynku_08  text,
    funszczegolowabudynku_09  text,
    funszczegolowabudynku_10  text,
    liczbakondygnacji      text,
    kodkst                 text,
    nazwa                  text,
    zabytek                text,
    geometry               text,
    powiat                 text
);

create table if not exists bdot.lookup_funogolnabudynku (
   funogolnabudynku        text primary key,
   funkcja_ogolna_budynku  text not null
);

create table if not exists bdot.lookup_funszczegolowabudynku (
   funszczegolowabudynku        text primary key,
   funkcja_szczegolowa_budynku  text not null
);

create table if not exists bdot.lookup_x_katistnienia (
   x_katistnienia          text primary key,
   status_bdot             text not null
);

create table if not exists bdot.lookup_x_kod (
   x_kod                   text primary key,
   kategoria_bdot          text not null
);

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
    WHERE lokalnyid ~ E'^[[:xdigit:]]{8}-([[:xdigit:]]{4}-){3}[[:xdigit:]]{12}$' -- check if uuid is valid
;


INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1110', 'budynki mieszkalne jednorodzinne') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1121', 'budynki o dwóch mieszkaniach') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1122', 'budynki o trzech i więcej mieszkaniach') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1130', 'budynki zbiorowego zamieszkania') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1211', 'budynki hoteli') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1212', 'pozostałe budynki zakwaterowania turystycznego') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1220', 'budynki biurowe') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1230', 'budynki handlowo-usługowe') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1241', 'budynki łączności dworców i terminali') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1242', 'garaże') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1251', 'budynki przemysłowe') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1252', 'zbiorniki, silosy lub budynki magazynowe') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1261', 'ogólnodostępne budynki kulturalne') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1262', 'muzea lub biblioteki') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1263', 'budynki szkół i instytucji badawczych') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1264', 'budynki szpitali i zakładów opieki medyczne') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1265', 'budynki kultury fizycznej') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1271', 'budynki gospodarstwa rolnego') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1272', 'budynki kultu religijnego') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1273', 'budynek zabytkowy') on conflict do nothing;
INSERT INTO bdot.lookup_funogolnabudynku VALUES ('1274', 'pozostałe budynki niemieszkalne') on conflict do nothing;

INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1110.Dj', 'budynek jednorodzinny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1110.Dl', 'dom letniskowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1110.Ls', 'leśniczówka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1121.Db', 'budynek o dwóch mieszkaniach') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1122.Dw', 'budynek wielorodzinny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Bs', 'bursa szkolna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Db', 'dom dla bezdomnych') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Dd', 'dom dziecka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Os', 'dom opieki społecznej') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Dp', 'dom parafialny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Ds', 'dom studencki') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Dz', 'dom zakonny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Hr', 'hotel robotniczy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.In', 'internat') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Kl', 'klasztor') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Km', 'koszary') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Po', 'placówka opiekuńczo-wychowawcza') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Ra', 'rezydencja ambasadora') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Rb', 'rezydencja biskupia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Rp', 'rezydencja prezydencka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Zk', 'zakład karny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1130.Zp', 'zakład poprawczy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1211.Dw', 'dom weselny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1211.Ht', 'hotel') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1211.Mt', 'motel') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1211.Pj', 'pensjonat') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1211.Rj', 'restauracja') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1211.Zj', 'zajazd') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1212.Dk', 'domek kempingowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1212.Dr', 'dom rekolekcyjny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1212.Dw', 'dom wypoczynkowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1212.Os', 'ośrodek szkoleniowo wypoczynkowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1212.St', 'schronisko turystyczne') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Bk', 'bank') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Ck', 'centrum konferencyjne') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Km', 'Kuria Metropolitarna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Mn', 'ministerstwo') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Pd', 'placówka dyplomatyczna lub konsularna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Pc', 'policja') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Pk', 'prokuratura') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Pg', 'przejście graniczne') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Sd', 'sąd') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Sf', 'siedziba firmy lub firm') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Pw', 'Starostwo Powiatowe') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Sg', 'straż graniczna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Sp', 'straż pożarna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Uc', 'Urząd Celny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Ug', 'Urząd Gminy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Um', 'Urząd Miasta') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Umg', 'Urząd Miasta i Gminy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Mr', 'Urząd Marszałkowski') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Up', 'placówka operatora pocztowego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Uw', 'Urząd Wojewódzki') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1220.Ap', 'inny urząd administracji publicznej') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Ap', 'apteka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Ch', 'centrum handlowe') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Dh', 'dom towarowy lub handlowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Ht', 'hala targowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Hw', 'hala wystawowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Hm', 'hipermarket lub supermarket') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Ph', 'pawilon handlowo-usługowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.So', 'stacja obsługi pojazdów') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1230.Sp', 'stacja paliw') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Kk', 'budynek kontroli ruchu kolejowego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Kp', 'budynek kontroli ruchu powietrznego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Ct', 'centrum telekomunikacyjne') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Da', 'dworzec autobusowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Dk', 'dworzec kolejowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Dl', 'dworzec lotniczy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Hg', 'hangar') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Lm', 'latarnia morska') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Lk', 'lokomotywownia lub wagonownia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Kg', 'stacja kolejki górskiej lub wyciągu krzesełkowego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Rt', 'stacja nadawcza radia i telewizji') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Tp', 'terminal portowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Ab', 'zajezdnia autobusowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Tr', 'zajezdnia tramwajowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1241.Tb', 'zajezdnia trolejbusowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1242.Gr', 'garaż') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1242.Pw', 'parking wielopoziomowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.El', 'elektrociepłownia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Ek', 'elektrownia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Kt', 'kotłownia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Mn', 'młyn') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Pr', 'produkcyjny') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Rf', 'rafineria') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Ss', 'spalarnia śmieci') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Wr', 'warsztat remontowo-naprawczy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1251.Wt', 'wiatrak') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.Sp', 'budynek spedycji') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.Ch', 'chłodnia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.El', 'elewator') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.Mg', 'magazyn') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.Sl', 'silos') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.Gz', 'zbiornik na gaz') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1252.Ci', 'zbiornik na ciecz') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Oz', 'budynek ogrodu zoo lub botanicznego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Dk', 'dom kultury') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Fh', 'filharmonia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Hw', 'hala widowiskowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Ks', 'kasyno') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Kn', 'kino') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Kl', 'klub, dyskoteka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Op', 'opera') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Sz', 'schronisko dla zwierząt') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1261.Tt', 'teatr') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1262.Ar', 'archiwum') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1262.Bl', 'biblioteka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1262.Ci', 'centrum informacyjne') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1262.Gs', 'galeria sztuki') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1262.Mz', 'muzeum') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Ob', 'obserwatorium lub planetarium') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Pb', 'placówka badawcza') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Ps', 'przedszkole') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Sh', 'stacja hydrologiczna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Sm', 'stacja meteorologiczna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Sp', 'szkoła podstawowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Sd', 'szkoła ponadpodstawowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1263.Sw', 'szkoła wyższa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Hs', 'hospicjum') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Iw', 'izba wytrzeźwień') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Jr', 'jednostka ratownictwa medycznego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Kw', 'klinika weterynaryjna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Oo', 'ośrodek opieki społecznej') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Po', 'placówka ochrony zdrowia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.St', 'sanatorium') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Sk', 'stacja krwiodawstwa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Ss', 'stacja sanitarno-epidemiologiczna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Sz', 'szpital') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1264.Zb', 'żłobek') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Hs', 'hala sportowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Ht', 'halowy tor gokartowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Ks', 'klub sportowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Kt', 'korty tenisowe') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Kr', 'kręgielnia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Pl', 'pływalnia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Sg', 'sala gimnastyczna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.St', 'strzelnica') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Sl', 'sztuczne lodowisko') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1265.Uj', 'ujeżdżalnia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1271.Bg', 'budynek gospodarczy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1271.Bp', 'budynek produkcyjny zwierząt hodowlanych') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1271.St', 'stajnia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1271.Sz', 'szklarnia lub cieplarnia') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Bc', 'budynki cmentarne') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Ck', 'cerkiew') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Dp', 'dom pogrzebowy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Dz', 'dzwonnica') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Ir', 'inny budynek kultu religijnego') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Kp', 'kaplica') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Ks', 'kościół') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Kr', 'krematorium') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Mc', 'meczet') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1272.Sn', 'synagoga') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1273.Zb', 'zabytek bez funkcji użytkowej') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.As', 'areszt śledczy') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Bc', 'bacówka') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Sc', 'schronisko dla nieletnich') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Sg', 'stacja gazowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Sp', 'stacja pomp') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.St', 'stacja transformatorowa') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Tp', 'toaleta publiczna') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Zk', 'zabudowania koszarowe') on conflict do nothing;
INSERT INTO bdot.lookup_funszczegolowabudynku VALUES ('1274.Zp', 'zakład karny lub poprawczy') on conflict do nothing;

INSERT INTO bdot.lookup_x_katistnienia VALUES ('Eks', 'eksploatowany') on conflict do nothing;
INSERT INTO bdot.lookup_x_katistnienia VALUES ('Bud', 'w budowie') on conflict do nothing;
INSERT INTO bdot.lookup_x_katistnienia VALUES ('Zns', 'zniszczony') on conflict do nothing;
INSERT INTO bdot.lookup_x_katistnienia VALUES ('Tmc', 'tymczasowy') on conflict do nothing;
INSERT INTO bdot.lookup_x_katistnienia VALUES ('Ncn', 'nieczynny') on conflict do nothing;

INSERT INTO bdot.lookup_x_kod VALUES ('BUBD01', 'budynki mieszkalne jednorodzinne') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD02', 'budynki o dwóch mieszkaniach') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD03', 'budynki o trzech i więcej mieszkaniach') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD04', 'budynki zbiorowego zamieszkania') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD05', 'budynki hoteli') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD06', 'budynki zakwaterowania turystycznego, pozostałe') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD07', 'budynki biurowe') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD08', 'budynki handlowo-usługowe') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD09', 'budynki łączności, dworców i terminali') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD10', 'budynki garaży') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD11', 'budynki przemysłowe') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD12', 'zbiorniki, silosy i budynki magazynowe') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD13', 'ogólnodostępne obiekty kulturalne') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD14', 'budynki muzeów i bibliotek') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD15', 'budynki szkół i instytucji badawczych') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD16', 'budynki szpitali i zakładów opieki medycznej') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD17', 'budynki kultury fizycznej') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD18', 'budynki gospodarstw rolnych') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD19', 'budynki przeznaczone do sprawowania kultu religijnego i czynności religijnych') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD20', 'obiekty budowlane wpisane do rejestru zabytków i objęte indywidualną ochroną konserwatorską oraz nieruchome, archeologiczne dobra kultury') on conflict do nothing;
INSERT INTO bdot.lookup_x_kod VALUES ('BUBD21', 'pozostałe budynki niemieszkalne, gdzie indziej nie wymienione') on conflict do nothing;
