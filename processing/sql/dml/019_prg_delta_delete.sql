delete from prg.delta
where lokalnyid in (
    select delta.lokalnyid
    from prg.delta
    join prg.punkty_adresowe on delta.lokalnyid = punkty_adresowe.lokalnyid::uuid
    where (punkty_adresowe.waznydo is not null and punkty_adresowe.waznydo::timestamptz < now()) or punkty_adresowe.koniecwersjiobiektu is not null
);
