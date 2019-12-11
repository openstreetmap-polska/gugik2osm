#!/bin/bash

source .env

cd $(dirname $0)

now=$(date +"%Y%m%d")
logfile="OSM_Replication-$now.log"
logpath="logs/"

echo -e '\n-------------------START' >> $logpath$logfile 2>&1
date >> $logpath$logfile 2>&1

set -e

onexit() {
  local x=$?
  if [ $x -ne 0 ]; then
    tail -n 100 /home/osm/logs/$logfile|mail -s "Błąd replikacji danych OSM" linsysop@abakus.net.pl
  fi
    }

trap "onexit" exit

(
  # Try to lock on the lock file (fd 200)

  flock -x -n 200 || exit 0


  if [ ! -f current.osc ]; then
    echo "No current.osc file found, downloading new one..." >> $logpath$logfile 2>&1
    osmosis --read-replication-interval --write-xml-change current.osc >> $logpath$logfile 2>&1
  fi

  osm2pgsql \
    --number-processes 1 -v -C 1000 -G -K -j -x -s \
    -S ./gugik2osm.style --append -d $PGDATABASE --bbox 13.50,48.50,24.50,55.50  \
    current.osc >> $logpath$logfile 2>&1

  if [ "$?" = "0" ]; then
    echo "Success, removing current.osc" >> $logpath$logfile  2>&1
    rm current.osc >> $logpath$logfile  2>&1
    echo "Done" >> $logpath$logfile  2>&1
    psql -f postprocessing.sql $PGDATABASE
  else
    echo "ERROR - osm2pgsql failed"
  fi
) 200>/home/osm/scripts/osm/.replication.lock

date >> $logpath$logfile  2>&1
echo '-------------------STOP' >> $logpath$logfile 2>&1
