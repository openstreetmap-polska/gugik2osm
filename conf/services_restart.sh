#!/usr/bin/env bash

systemctl stop imposm
systemctl stop supervisor
systemctl stop airflow-webserver
systemctl stop airflow-scheduler
systemctl stop postgresql

systemctl start postgresql
systemctl start supervisor
systemctl start airflow-scheduler
systemctl start airflow-webserver
systemctl start imposm
