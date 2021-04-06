-- okreslenie nazwy ulic
-- zgodnosc simc, podobna nazwa ulicy

drop table if exists teryt.temp_ulic;

select
    pa.lokalnyid,
    teryt_msc, pa.ul,
    pa.ulic,
    pa.teryt_simc,
    simc_mapping.sym_czesc,
    null::text as teryt_ulic,
    null::text as teryt_ulica
into teryt.temp_ulic 
from
    prg.pa,
    (
        select simc.woj, simc.pow, simc.gmi, simc.sym, simc.sym as sym_czesc, simc.nazwa
        from teryt.simc
        where rodz_gmi not in ('8', '9')

        union

        select simc.woj, simc.pow, simc.gmi, x.sym, simc.sym as sym_czesc, simc.nazwa
        from
            teryt.simc as simc,
            (
                select woj, pow, '01'::text as gmi, sym
                from teryt.simc
                where rodz_gmi in ('8', '9')
                group by woj, pow, sym
            ) as x
        where simc.woj = x.woj and simc.pow = x.pow and simc.gmi = x.gmi
    ) as simc_mapping
where 1=1
    and pa.teryt_simc = simc_mapping.sym
    and teryt_ulica is null
    and ul is not null
;

create index if not exists idx_teryt_ulic_sym on teryt.ulic using hash (sym);

update teryt.temp_ulic 
set teryt_ulic = (
	select ul.sym_ul
	from teryt.ulic as ul
	where ul.sym = sym_czesc and similarity(ul, ul.nazwa_1) >= 0.3
	order by similarity(ul, ul.nazwa_1) desc
	limit 1
);

update teryt.temp_ulic 
set teryt_ulica = trim(concat(trim(cm.m), ' ', trim(ul.nazwa_2),  ' ', trim(ul.nazwa_1)))
from teryt.ulic as ul, teryt.cecha_mapping cm
where ul.sym = sym_czesc and ul.sym_ul = teryt_ulic and ul.cecha = cm.cecha
;

update prg.pa as pa
set teryt_ulica = t.teryt_ulica, teryt_ulic = t.teryt_ulic
from teryt.temp_ulic as t
where pa.lokalnyid = t.lokalnyid
;

drop table if exists teryt.temp_ulic;

drop index teryt.idx_teryt_ulic_sym ;

analyze prg.pa;
