echo "Running flake8..."
flake8 ./app --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 ./tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 ./processing --count --select=E9,F63,F7,F82 --show-source --statistics

echo "Running pytest..."
python -m pytest

echo "Running great_expectations..."
python ./great_expectations/check_street_names_mappings.py ./processing/sql/data/street_names_mappings.csv

echo "Launching Docker container with PostgreSQL+Postgis..."
docker run --name "gugik2osm-postgresql-for-testing" --shm-size=4g -v $pwd/processing/sql:/sql `
  -e MAINTAINANCE_WORK_MEM=512MB -p 15432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASS=1234 `
  -e POSTGRES_DBNAME=gis -e SCHEMA_NAME=bdot,teryt,prg,changesets_processing -d --rm -t kartoza/postgis

echo "Pausing for 10s to let docker start..."
Start-Sleep -s 10

echo "Creating required table..."
docker exec gugik2osm-postgresql-for-testing runuser -l postgres -c 'psql -d gis -f /sql/ddl/001_table_definitions.sql'
docker exec gugik2osm-postgresql-for-testing runuser -l postgres -c 'psql -d gis -f /sql/ddl/002_views.sql'
docker exec gugik2osm-postgresql-for-testing runuser -l postgres -c 'psql -d gis -f /sql/ddl/003_functions.sql'
docker exec gugik2osm-postgresql-for-testing runuser -l postgres -c 'psql -d gis -f /sql/ddl/004_inserts_with_default_data.sql'
echo "DB ready."

echo "Running SQL processing scripts to see if there will be any error..."
python ./processing/scripts/prg_prepare.py --full --dsn "host=localhost port=15432 dbname=gis user=postgres password=1234"
python ./processing/scripts/prg_prepare.py --update --dsn "host=localhost port=15432 dbname=gis user=postgres password=1234"

echo "Removing docker container..."
docker stop gugik2osm-postgresql-for-testing

echo "Finished removing docker container."

echo "======================================================================"
echo "Done."
