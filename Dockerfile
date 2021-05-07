FROM python:3.8

RUN apt-get update -y
RUN apt-get install -y nginx supervisor

# create folder structure similar to the one on production server
RUN mkdir /opt/gugik2osm
RUN mkdir /opt/gugik2osm/app
RUN mkdir /opt/gugik2osm/web
RUN mkdir /opt/gugik2osm/log
WORKDIR /opt/gugik2osm

# copy files to docker and install python libraries
COPY ./requirements.txt ./
RUN python -m venv /opt/gugik2osm/venv
ENV VIRTUAL_ENV /opt/gugik2osm/venv
ENV PATH /opt/gugik2osm/venv/bin:$PATH
RUN pip install --no-cache-dir -r requirements.txt

COPY ./processing/ ./git/processing/
COPY ./conf/ ./conf/

# create symlinks similar to the ones on production server
RUN ln -sf /opt/gugik2osm/conf/nginx.conf /etc/nginx/sites-available/gugik2osm.conf
RUN ln -sf /opt/gugik2osm/conf/nginx.conf /etc/nginx/sites-enabled/gugik2osm.conf
# remove default dir so we can create a symlink
RUN rm -rf /var/www/html
RUN ln -sf /opt/gugik2osm/web /var/www/html
RUN ln -sf /opt/gugik2osm/conf/supervisord.conf /etc/supervisor/conf.d/gugik2osm.conf
# remove default nginx config
RUN rm /etc/nginx/sites-enabled/default
RUN rm /etc/nginx/sites-available/default
# make directory for socket used by gunicorn
RUN mkdir /run/gugik2osm/
# make directory for overpass layers
RUN mkdir /var/www/overpass-layers/

# change placeholder dsn in supervisord config
RUN sed -i "s/dsn=\"host=localhost port=5432 user=user password=password dbname=db\",reCaptchaSecretToken=\"\"/dsn=\"%(ENV_dsn)s\",reCaptchaSecretToken=\"%(ENV_reCaptchaSecretToken)s\"/" /opt/gugik2osm/conf/supervisord.conf

# create a script starting services and keeping container running (bash will wait for commands)
RUN echo "supervisord && service nginx restart && bash" > ./start.sh

CMD ["bash", "./start.sh"]
