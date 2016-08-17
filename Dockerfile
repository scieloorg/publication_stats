FROM python:3.5.2

COPY requirements.txt /app/requirements.txt
COPY production.ini-TEMPLATE /app/production.ini-TEMPLATE
COPY docker/generate_production_ini.py /app/docker/generate_production_ini.py
COPY docker/entrypoint.sh /app/docker/entrypoint.sh

WORKDIR /app

RUN pip install -r requirements.txt
RUN python docker/generate_production_ini.py

ENV PUBLICATIONSTATS_SETTINGS_FILE=/app/production.ini

EXPOSE 11620
EXPOSE 8000

ADD docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]