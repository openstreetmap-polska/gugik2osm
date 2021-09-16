create schema if not exists changesets_processing;
CREATE TABLE IF NOT EXISTS changesets_processing.processed_files (
    file_path text not null primary key,
    inserted_at timestamp with time zone not null default CURRENT_TIMESTAMP
);
create index if not exists idx_processed_files_ts_inserted on changesets_processing.processed_files (inserted_at);
CREATE TABLE IF NOT EXISTS changesets_processing.changesets (
    file_path text not null,
    changeset_id integer not null,
    created_at timestamp with time zone not null,
    closed_at timestamp with time zone,
    open boolean,
    num_changes integer,
    osm_user text not null,
    uid integer not null,
    comments_count integer,
    tags jsonb,
    bbox geometry(Polygon, 4326),
    primary key (file_path, changeset_id),
    foreign key (file_path) REFERENCES changesets_processing.processed_files ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);
-- create index if not exists idx_changesets_ts on changesets_processing.changesets using brin (created_at) with (pages_per_range=64, autosummarize = on);
create index if not exists idx_changesets_ts_created on changesets_processing.changesets (created_at);
create index if not exists idx_changesets_ts_closed on changesets_processing.changesets (closed_at);
create index if not exists idx_changesets_geom on changesets_processing.changesets using gist (bbox);
