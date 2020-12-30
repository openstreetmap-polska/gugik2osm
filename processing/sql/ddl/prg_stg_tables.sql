CREATE unlogged TABLE if not exists prg.jednostki_administracyjne (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    nazwa text,
    idteryt text,
    poziom text,
    jednostkapodzialuteryt text
);

CREATE unlogged TABLE if not exists prg.miejscowosci (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    nazwa text,
    idteryt text,
    geometry text,
    miejscowosc text
);

CREATE unlogged TABLE if not exists prg.punkty_adresowe (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    jednostkaadministracyjna text,
    jednostkaadministracyjna_01 text,
    jednostkaadministracyjna_02 text,
    jednostkaadministracyjna_03 text,
    miejscowosc text,
    czescmiejscowosci text,
    ulica text,
    numerporzadkowy text,
    kodpocztowy text,
    status text,
    geometry text,
    komponent text,
    komponent_01 text,
    komponent_02 text,
    komponent_03 text,
    komponent_04 text,
    komponent_05 text,
    komponent_06 text,
    obiektemuia text
);

CREATE unlogged TABLE if not exists prg.ulice (
    gmlid text,
    identifier text,
    lokalnyid text,
    przestrzennazw text,
    wersjaid text,
    poczatekwersjiobiektu text,
    koniecwersjiobiektu text,
    waznyod text,
    waznydo text,
    nazwaglownaczesc text,
    idteryt text,
    geometry text,
    ulica text
);
