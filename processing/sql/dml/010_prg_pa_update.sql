set jit=on;
-- aktualizacja nazwy miejscowosci na podstawie simc
update prg.pa as pa
set teryt_msc = simc.nazwa
from teryt.simc as simc
where pa.teryt_simc = simc.sym;

analyze prg.pa;
