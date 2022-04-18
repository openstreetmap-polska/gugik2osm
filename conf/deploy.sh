#!/bin/bash

# exit on error in any command
set -e

cd /opt/gugik2osm/git/
git pull

source /opt/gugik2osm/venv/bin/activate

pip3 install -r /opt/gugik2osm/git/requirements.txt

rsync --verbose --recursive --delete --exclude "__pycache__" /opt/gugik2osm/git/app/ /opt/gugik2osm/app/
rsync --verbose --recursive --delete --exclude "__pycache__" /opt/gugik2osm/git/web/ /opt/gugik2osm/web/

cp /opt/gugik2osm/git/conf/*.sh /opt/gugik2osm/conf/
cp /opt/gugik2osm/git/conf/*.service /opt/gugik2osm/conf/
chmod 775 /opt/gugik2osm/conf/*.sh
chmod 775 /opt/gugik2osm/git/processing/bash/*.sh
sudo cp /opt/gugik2osm/git/conf/cronfile /opt/gugik2osm/conf/
cp /opt/gugik2osm/git/conf/nginx.conf /opt/gugik2osm/conf/

rsync --verbose --recursive --delete --exclude "__pycache__" /opt/gugik2osm/git/airflow/dags/ /opt/gugik2osm/airflow/dags/
# rsync --verbose --recursive --delete --exclude "__pycache__" /opt/gugik2osm/git/airflow/plugins/ /opt/gugik2osm/airflow/plugins/

cp /opt/gugik2osm/git/imposm3/mapping.yaml /opt/gugik2osm/imposm3/
cp /opt/gugik2osm/git/imposm3/poland.geojson /opt/gugik2osm/imposm3/
cp /opt/gugik2osm/git/imposm3/imposm.service /opt/gugik2osm/imposm3/
sudo cp /opt/gugik2osm/imposm3/imposm.service /etc/systemd/system/imposm.service
sudo chmod 600 /etc/systemd/system/imposm.service
sudo cp /opt/gugik2osm/conf/create_socket_folder.service /etc/systemd/system/create_socket_folder.service
sudo chmod 600 /etc/systemd/system/create_socket_folder.service
sudo systemctl daemon-reload
sudo service nginx restart

python3 /opt/gugik2osm/git/processing/scripts/overpass2geojson.py --input-dir /opt/gugik2osm/git/processing/overpass/ --output-dir /var/www/overpass-layers/ --skip-existing

bash /opt/gugik2osm/conf/deploy_street_names_mappings.sh
