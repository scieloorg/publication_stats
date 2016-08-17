# coding: utf-8
import os
from configparser import ConfigParser

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WEBAPP_PORT = '8000'  # ver ports: docker-compose.yml e Dockerfile
production_template_ini_filepath = os.path.join(PROJECT_PATH + '/production.ini-TEMPLATE')
new_production_ini_filepath = os.path.join(PROJECT_PATH + '/production.ini')
config = ConfigParser()
config.read_file(open(production_template_ini_filepath))
config.set('app:main', 'elasticsearch', os.environ.get('ELASTICSEARCH', 'esd.scielo.org:9200'))
config.set('app:main', 'articlemeta', os.environ.get('ARTICLEMETA', 'esd.scielo.org:9200'))
config.set('server:main', 'port', WEBAPP_PORT)

with open(new_production_ini_filepath, 'w') as configfile:    # save
    config.write(configfile)
