#!/bin/bash
set -e

# inicia o webserver:
cd /app
gunicorn --paste production.ini -w 4 -b 0.0.0.0 --daemon

# inicia o thirft server
publicationstats_thriftserver --port 11620 --host 0.0.0.0