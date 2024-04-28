#!/usr/bin/env bash

# exit on error in any command
set -e

mv /opt/gugik2osm/web/index.html /opt/gugik2osm/web/index_old.html
mv /opt/gugik2osm/web/maintenance.html /opt/gugik2osm/web/index.html

set -a
source /opt/gugik2osm/conf/.env
set +a

query=$(cat << EOF
UPDATE process_locks
SET (
        in_progress,
        start_time,
        end_time
    ) = (
        true,
        CURRENT_TIMESTAMP,
        null
    )
WHERE process_name = 'db_lock'
;
EOF
)

psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "$query"
