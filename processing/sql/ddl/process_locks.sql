create table if not exists process_locks (
  process_name text primary key,
  in_progress boolean not null
);

insert into process_locks values ('prg_full_update', false) on conflict do nothing;
