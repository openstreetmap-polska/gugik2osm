#!/usr/bin/env bash

/opt/gugik2osm/imposm3/imposm-0.11.1-linux-x86-64/imposm import -config /opt/gugik2osm/imposm3/config.json -read /opt/gugik2osm/imposm3/poland-latest.osm.pbf -overwritecache -write -diff -deployproduction
