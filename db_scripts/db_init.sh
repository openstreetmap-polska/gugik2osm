#!/bin/bash

# Sprawdzenia

if [ ! -f .env ]; then
  echo "Brak pliku ze zmiennymi środowiska !!!!"
  exit 1
fi

# Pobieramy zmienne środowiskowe z zewnętrznego pliku (żeby nie przechowywać haseł w repo)
source .env

# Zmienne
user=$PGUSER
passwd=$PGPASSWORD
database=$PGDATABASE
host=$PGHOSTADDR
extract="poland-latest.osm.pbf"
extract_srv="http://download.geofabrik.de/europe/"
import_cache=4000
import_processes=4

sudo -u postgres psql -c "create user $user login superuser password '$passwd';"
sudo -u postgres psql -c "create database $database owner $user;"

psql -c "create extension postgis;" $database
psql -c "create extension hstore;" $database

wget "$extract_srv$extract"

osm2pgsql \
  --create \
  --database $database \
  --merc \
  --slim \
  --cache $import_cache \
  --username $user \
  --host $host \
  --number-processes $import_processes \
  --style gugik2osm.style \
  $extract

rm $extract