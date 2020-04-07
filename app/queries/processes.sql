select
    coalesce(pretty_name, process_name) process_name,
    in_progress,
    to_char(start_time at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') start_time,
    to_char(end_time at time zone 'Europe/Warsaw', 'YYYY-MM-DD HH24:MI:SS') end_time,
    no_of_tiles_to_process,
    process_name process_abbr_name
from process_locks pl
left join (
    select count(*) no_of_tiles_to_process from expired_tiles where not processed
) t on pl.process_name = 'prg_partial_update'
left join (
    select 'prg_full_update' process_name, 'Cotygodniowa aktualizacja danych PRG' pretty_name
    union all
    select 'prg_partial_update' process_name, 'Cominutowa aktualizacja danych' pretty_name
    union all
    select 'teryt_update' process_name, 'Codzienna aktualizacja danych TERYT' pretty_name
) n using (process_name)
;
