create table if not exists expired_tiles (
    file_name text not null,
    z int not null,
    x int not null,
    y int not null,
    processed bool not null default false,
    constraint expired_tiles_pk primary key (file_name, z, x, y)
);

alter table expired_tiles add column if not exists created_at timestamp with time zone;
alter table expired_tiles alter column created_at set default CURRENT_TIMESTAMP;
create index if not exists idx_expired_tiles_created_ts on expired_tiles(created_at desc nulls last);

create index if not exists idx_expired_tiles_not_processed on expired_tiles(processed) where not processed;
