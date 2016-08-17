#!/bin/bash
set -e

# inicia o webserver:
cd /app
pserve production.ini --daemon

# inicia o thirft server
publicationstats_thriftserver --port 11620 --host 0.0.0.0