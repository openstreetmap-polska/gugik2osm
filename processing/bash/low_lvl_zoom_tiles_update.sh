#!/bin/bash

# exit on error in any command
set -e

set -a
source /opt/gugik2osm/conf/.env
set +a

in_progress_count=$( psql -X -A -t -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "SELECT COUNT (*) FROM process_locks where in_progress=true" )

if [ "in_progress_count" -eq 0 ]; then
  echo "updating tiles on zoom levels 6 and 7" >> /opt/gugik2osm/log/prg_processing.log
  psql -h $PGHOSTADDR -p $PGPORT -d $PGDATABASE -U $PGUSER -c "create temporary table tt (z int, x int, y int, mvt bytea); \
    insert into tt select z, x, y, mvt(z, x, y) from tiles where z in (6, 7); \
    analyze tt; \
    update tiles set mvt = tt.mvt from tt where tiles.z=tt.z and tiles.x=tt.x and tiles.y=tt.y; \
    drop table tt; \
  " >> /opt/gugik2osm/log/prg_processing.log 2>&1
  echo "done updating tiles on zoom levels 6 and 7" >> /opt/gugik2osm/log/prg_processing.log
else
  echo "some process in progress... skipping updating tiles on zoom levels 6 and 7" >> /opt/gugik2osm/log/prg_processing.log
fi
