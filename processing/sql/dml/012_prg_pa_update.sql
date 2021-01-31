-- okreslenie nazwy ulic
-- zgodnosc simc, kod nazwy ulicy
update prg.pa as pa
set teryt_ulica = trim(concat(cm.m, ' ', (u1.nazwa_2 || ' '), u1.nazwa_1)), teryt_ulic = u1.sym_ul
from teryt.ulic as u1, teryt.cecha_mapping cm,
(select simc.woj, simc.pow, simc.gmi, simc.sym, simc.sym as sym_czesc, simc.nazwa
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

where pa.teryt_simc = simc_mapping.sym and simc_mapping.sym_czesc = u1.sym 
	and pa.ulic = u1.sym_ul 
	and u1.cecha = cm.cecha
	and teryt_ulica is null;