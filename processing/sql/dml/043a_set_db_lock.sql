UPDATE process_locks
SET (
        in_progress,
        start_time,
        end_time
    ) = (
        true,
        CURRENT_TIMESTAMP,
        null
    )
WHERE process_name = 'db_lock'
;
