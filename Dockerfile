FROM python:3.7
RUN alias python3.7="python3"

RUN apt-get update -y
RUN apt-get install -y nginx supervisor

# create folder structure similar to the one on production server
RUN mkdir /opt/gugik2osm
RUN mkdir /opt/gugik2osm/app
RUN mkdir /opt/gugik2osm/web
WORKDIR /opt/gugik2osm

# copy files to docker and install python libraries
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./processing/ ./processing/
COPY ./conf/ ./conf/
COPY ./app/ ./app/
COPY ./web/ ./web/

# remove placeholder dsn in supervisord config
RUN sed -i "/dsn=\"host=localhost port=5432 user=user password=password dbname=db\"/d" /opt/gugik2osm/conf/supervisord.conf

# create symlinks similar to the ones on production server
RUN ln -sf /opt/gugik2osm/conf/nginx.conf /etc/nginx/sites-available/gugik2osm.conf
RUN ln -sf /opt/gugik2osm/conf/nginx.conf /etc/nginx/sites-enabled/gugik2osm.conf
# remove default dir so we can create a symlink
RUN rm -rf /var/www/html
RUN ln -sf /opt/gugik2osm/web /var/www/html
RUN ln -sf /opt/gugik2osm/conf/supervisord.conf /etc/supervisor/conf.d/gugik2osm.conf

# create a script starting services and keeping container running (bash will wait for commands)
RUN echo "service supervisor restart && service nginx restart && bash" > ./start.sh

CMD ["bash", "./start.sh"]
