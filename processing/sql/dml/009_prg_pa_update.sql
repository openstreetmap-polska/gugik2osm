-- aktualizacja simc na podstawie terytu
-- jezeli nadal simc jest nieokreslone, to wybieramy na zasadzie podobienstwa nazwy miejscowosci
update prg.pa
set teryt_simc = (
	select simc.sym
	from teryt.simc as simc
	where terc6 = simc.woj || simc.pow || simc.gmi and similarity(simc.nazwa, pa.msc) >= 0.3
	order by similarity(simc.nazwa, pa.msc) desc
	limit 1
	)
where pa.teryt_simc is null;