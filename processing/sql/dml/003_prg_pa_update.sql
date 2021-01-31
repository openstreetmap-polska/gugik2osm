-- aktualizacja simc na podstawie terytu
-- zgodnosc po woj, pow, gmi, rodz_gmi, simc, nazwa
update prg.pa as pa 
set teryt_simc = sym
from teryt.simc as simc
where pa.teryt7 = simc.woj || simc.pow || simc.gmi || simc.rodz_gmi and lower(replace(simc.nazwa, ' ', '')) = lower(replace(pa.msc, ' ', '')) and pa.simc = simc.sym;
