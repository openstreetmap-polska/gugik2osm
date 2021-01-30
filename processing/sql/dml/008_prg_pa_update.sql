-- aktualizacja simc na podstawie terytu
--dla calej reszty zakladamy ze punkty_adresowe.simc jest poprawne
update prg.pa as pa
set teryt_simc = pa.simc
where teryt_simc is null;