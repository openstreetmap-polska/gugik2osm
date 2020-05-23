create table if not exists expired_tiles (
    file_name text not null,
    z int not null,
    x int not null,
    y int not null,
    processed bool not null default false,
    constraint expired_tiles_pk primary key (file_name, z, x, y)
);
