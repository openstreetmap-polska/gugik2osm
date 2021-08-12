create table if not exists package_exports (
  export_id bigint generated by default as identity,
  created_at timestamp with time zone not null default CURRENT_TIMESTAMP,
  bbox geometry(geometry, 3857) not null,
  adresy int,
  budynki int
);

create index if not exists idx_package_exports_created_at on package_exports(created_at);
