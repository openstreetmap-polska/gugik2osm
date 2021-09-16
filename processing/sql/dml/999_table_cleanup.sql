delete from expired_tiles where processed and created_at < (CURRENT_TIMESTAMP - INTERVAL '7 days');
--vacuum analyze expired_tiles ;
