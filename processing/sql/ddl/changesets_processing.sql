create schema if not exists changesets_processing;
CREATE TABLE IF NOT EXISTS changesets_processing.processed_files (file_path text not null primary key);
CREATE TABLE IF NOT EXISTS changesets_processing.changesets (
    file_path text not null,
    changeset_id integer not null,
    created_at timestamp with time zone not null,
    closed_at timestamp with time zone,
    open boolean,
    num_changes integer,
    osm_user text not null,
    uid integer not null,
    min_lat real,
    min_lon real,
    max_lat real,
    max_lon real,
    comments_count integer,
    tags jsonb,
    bbox geometry(Polygon, 4326),
    primary key (file_path, changeset_id)
);
-- create index if not exists idx_changesets_ts on changesets_processing.changesets using brin (created_at) with (pages_per_range=64, autosummarize = on);
create index if not exists idx_changesets_ts on changesets_processing.changesets (created_at);
create index if not exists idx_changesets_geom on changesets_processing.changesets using gist (bbox);
