create table if not exists expired_tiles (
    file_name text not null,
    z int not null,
    x int not null,
    y int not null,
    processed bool not null default false,
    created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
    constraint expired_tiles_pk primary key (file_name, z, x, y)
);

create index if not exists idx_expired_tiles_created_ts on expired_tiles(created_at);
create index if not exists idx_expired_tiles_not_processed on expired_tiles(processed) where not processed;
