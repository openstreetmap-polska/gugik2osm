set jit=on;
-- aktualizacja simc na podstawie terytu
-- zgodnosc po woj, pow, gmi, miejscowość podstawowa (tm = '01'), nazwa

update prg.pa as pa
set teryt_simc = sym
from teryt.simc as simc
where 1=1
    and terc6 = simc.woj || simc.pow || simc.gmi
    and lower(replace(simc.nazwa, ' ', '')) = lower(replace(pa.msc, ' ', ''))
    and simc.rm = '01' and teryt_simc is null
;

analyze prg.pa;
