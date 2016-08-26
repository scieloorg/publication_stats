#!/bin/bash
set -e

python docker/generate_production_ini.py

# inicia o webserver e o thrift server:
/usr/bin/supervisord