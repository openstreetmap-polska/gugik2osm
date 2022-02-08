set jit=on;

delete from prg.delta_new
where lokalnyid in (
    select delta_new.lokalnyid
    from prg.delta_new
    join prg.punkty_adresowe on delta_new.lokalnyid = punkty_adresowe.lokalnyid::uuid
    where (punkty_adresowe.waznydo is not null and punkty_adresowe.waznydo::timestamptz < now()) or punkty_adresowe.koniecwersjiobiektu is not null
);
analyze prg.delta_new;
