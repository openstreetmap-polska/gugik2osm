-- aktualizacja simc na podstawie terytu
--dla calej reszty zakladamy ze punkty_adresowe.simc jest poprawne
update prg.pa as pa
set teryt_simc = pa.simc
where pa.simc similar to '[0-9]{7}' and pa.simc <> '0000000' and teryt_simc is null;