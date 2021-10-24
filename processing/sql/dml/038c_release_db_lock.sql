UPDATE process_locks
SET (
        in_progress,
        end_time,
        last_status
    ) = (
        false,
        CURRENT_TIMESTAMP,
        'SUCCESS'
    )
WHERE process_name = 'db_lock'
;
