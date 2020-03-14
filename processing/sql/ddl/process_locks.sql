create table if not exists process_locks (
  process_name text primary key,
  in_progress boolean not null
);

alter table process_locks add column if not exists start_time timestamp with time zone;
alter table process_locks add column if not exists end_time timestamp with time zone;

insert into process_locks values ('prg_full_update', false, null, null) on conflict do nothing;
insert into process_locks values ('teryt_update', false, null, null) on conflict do nothing;
