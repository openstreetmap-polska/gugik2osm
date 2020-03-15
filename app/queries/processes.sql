select *
from process_locks pl
left join (
    select count(*) no_of_tiles_to_process from expired_tiles where not processed
) t on pl.process_name = 'prg_partial_update'
;
