-- replace all duplicate words using regex expressions
-- so: 'plac Plac Mickiewicza' would become 'plac Mickiewicza'
update prg.pa
set teryt_ulica = regexp_replace(teryt_ulica, '\m(\w+)(?:\W+\1\M)+', '\1', 'i')
where teryt_ulica ~* '\m(\w+)(?:\W+\1\M)+'
;
