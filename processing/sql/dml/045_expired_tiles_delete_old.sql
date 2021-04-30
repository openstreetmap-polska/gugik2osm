delete from expired_tiles where processed=true and created_at < (CURRENT_TIMESTAMP - interval '7 days');
