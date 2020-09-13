#!/bin/bash

service imposm stop
service supervisor stop
service postgresql stop
service postgresql start
service supervisor start
service imposm start
