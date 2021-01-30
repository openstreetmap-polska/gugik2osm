-- okreslenie nazwy ulic
-- zgodnosc simc, nazwa ulicy (nazwa_1)
update prg.pa as pa
set teryt_ulica_2 = trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)), teryt_ulic_2 = u1.sym_ul, match_type = 3
from teryt.ulic as u1, teryt.cecha_mapping cm,
(select simc.woj, simc.pow, simc.gmi, simc.sym as sym_czesc, simc.sym, simc.nazwa
from teryt.simc
where rodz_gmi not in ('8', '9')
union
select simc.woj, simc.pow, simc.gmi, x.sym, simc.sym as sym_czesc, simc.nazwa
from teryt.simc as simc, (
	select woj, pow, '01'::text as gmi, sym
	from teryt.simc
	where rodz_gmi in ('8', '9')
	group by woj, pow, sym) as x
	where simc.woj = x.woj and simc.pow = x.pow and simc.gmi = x.gmi) as simc_mapping

where pa.teryt_simc_2 = simc_mapping.sym and simc_mapping.sym_czesc = u1.sym 
	and lower(replace(pa.ul, ' ', '')) = lower(replace(u1.nazwa_1, ' ', '')) 
	and u1.cecha = cm.cecha
	and teryt_ulica_2 is null;