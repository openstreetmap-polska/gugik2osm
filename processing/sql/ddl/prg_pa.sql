drop table if exists prg.pa;
create table prg.pa (
	lokalnyid uuid primary key,
	woj text,
	pow text,
	gmi text,
	terc6 text,
	msc text not null,
	simc text,
	ul text,
	ulic text,
	numerporzadkowy text not null,
	nr text not null,
	pna text,
	gml geometry,
	teryt_msc text,
	teryt_simc text,
	teryt_ulica text,
	teryt_ulic text
);

