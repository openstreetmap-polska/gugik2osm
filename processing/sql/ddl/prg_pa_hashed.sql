drop table if exists prg.pa_hashed;
create table prg.pa_hashed (
    hash text primary key,
    lokalnyid uuid not null,
    geom geometry not null
);