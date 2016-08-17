FROM python:3.5.2

COPY requirements.txt /app/requirements.txt
COPY production.ini-TEMPLATE /app/production.ini-TEMPLATE
COPY docker/generate_production_ini.py /app/docker/generate_production_ini.py

WORKDIR /app

RUN pip install -r requirements.txt
RUN python docker/generate_production_ini.py

ENV PUBLICATIONSTATS_SETTINGS_FILE=/app/production.ini

EXPOSE 11620

CMD publicationstats_thriftserver --port 11620 --host 0.0.0.0