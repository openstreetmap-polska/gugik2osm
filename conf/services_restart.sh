#!/bin/bash

service imposm stop
service supervisor stop
service airflow-webserver stop
service airflow-scheduler stop
service pgbouncer stop
service postgresql stop
service postgresql start
service pgbouncer start
service supervisor start
service airflow-scheduler start
service airflow-webserver start
service imposm start
