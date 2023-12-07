COPY (
    select *
    from prg.pa
) TO STDOUT
WITH CSV HEADER ENCODING 'UTF-8'
