create table if not exists exclude_prg (
  id uuid primary key
);

create table if not exists exclude_lod1 (
  id int primary key
);

alter table exclude_prg add column if not exists created_at timestamp with time zone;
alter table exclude_prg alter column created_at set default CURRENT_TIMESTAMP;
create index if not exists idx_exclude_prg_created_ts on exclude_prg(created_at desc nulls last);

alter table exclude_lod1 add column if not exists created_at timestamp with time zone;
alter table exclude_lod1 alter column created_at set default CURRENT_TIMESTAMP;
create index if not exists idx_exclude_lod1_created_ts on exclude_lod1(created_at desc nulls last);

create table if not exists exclude_prg_queue (
  id uuid primary key,
  created_at timestamp with time zone default CURRENT_TIMESTAMP,
  processed bool not null default false
);

create table if not exists exclude_lod1_queue (
  id int primary key,
  created_at timestamp with time zone default CURRENT_TIMESTAMP,
  processed bool not null default false
);
