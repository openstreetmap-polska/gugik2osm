rm -rf /opt/gugik2osm/git/
mkdir /opt/gugik2osm/git/
git clone https://github.com/openstreetmap-polska/gugik2osm.git /opt/gugik2osm/git/

sudo -H python3.7 -m pip install -r /opt/gugik2osm/git/requirements.txt

cp -r /opt/gugik2osm/git/app/* /opt/gugik2osm/app/
rm -r /opt/gugik2osm/web/*
cp -r /opt/gugik2osm/git/web/* /opt/gugik2osm/web/

cp /opt/gugik2osm/git/conf/*.sh /opt/gugik2osm/conf/
chmod 775 /opt/gugik2osm/conf/*.sh
sudo cp /opt/gugik2osm/git/conf/cronfile /opt/gugik2osm/conf/
cp /opt/gugik2osm/git/conf/*.conf /opt/gugik2osm/conf/

cp /opt/gugik2osm/git/imposm3/mapping.yaml /opt/gugik2osm/imposm3/
cp /opt/gugik2osm/git/imposm3/poland.geojson /opt/gugik2osm/imposm3/
cp /opt/gugik2osm/git/imposm3/imposm.service /opt/gugik2osm/imposm3/
sudo cp /opt/gugik2osm/imposm3/imposm.service /etc/systemd/system/imposm.service
sudo chmod 600 /etc/systemd/system/imposm.service
sudo systemctl daemon-reload
