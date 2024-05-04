#!/usr/bin/env bash
set -e

cd /opt/gugik2osm/git
git fetch origin main
git reset --hard "origin/main"

cd /opt/gugik2osm
source venv/bin/activate
pip3 install -r git/requirements.txt

rsync --verbose --recursive --delete --exclude "__pycache__" git/app/ app/
rsync --verbose --recursive --delete --exclude "__pycache__" git/web/ web/

cp git/conf/*.sh conf
cp git/conf/*.service conf

chmod 775 conf/*.sh
chmod 775 git/processing/bash/*.sh

rsync --verbose --recursive --delete --exclude "__pycache__" git/airflow/dags/ airflow/dags/
# rsync --verbose --recursive --delete --exclude "__pycache__" git/airflow/plugins/ airflow/plugins/

cp git/imposm3/mapping.yaml imposm3
cp git/imposm3/poland.geojson imposm3
cp git/imposm3/imposm.service /etc/systemd/system
cp conf/create_socket_folder.service /etc/systemd/system

chmod 600 /etc/systemd/system/imposm.service
chmod 600 /etc/systemd/system/create_socket_folder.service

systemctl daemon-reload

sudo --preserve-env=PATH -u ttaras python3 git/processing/scripts/overpass2geojson.py \
    --input-dir git/processing/overpass \
    --output-dir /var/www/overpass-layers \
    --skip-existing

sudo -u ttaras bash conf/deploy_street_names_mappings.sh
