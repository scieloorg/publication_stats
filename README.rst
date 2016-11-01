Publication Stats
=================

Web API and RPC Server to retrieve statistics from the documents and journals published at
the SciELO Network databases.

Build Status
============

.. image:: https://travis-ci.org/scieloorg/publication_stats.svg
    :target: https://travis-ci.org/scieloorg/publication_stats

Docker
======

Status
------

.. image:: https://images.microbadger.com/badges/image/scieloorg/publication_stats.svg
    :target: https://hub.docker.com/r/scieloorg/publication_stats
    
.. image:: https://images.microbadger.com/badges/version/scieloorg/publication_stats.svg
    :target: https://hub.docker.com/r/scieloorg/publication_stats

Como utilizar esta imagem
-------------------------

$ docker run --name my-publication_stats -d my-publication_stats

Como configurar o ELASTICSEARCH_HOST

$ docker run --name my-publication_stats -e ELASTICSEARCH=my_eshost:27017 -d my-publication_stats

Os serviços ativos nesta imagem são:

Web API: 127.0.0.1:8000
Thrift Server: 127.0.0.1:11620

É possível mapear essas portas para o hosting dos containers da seguinte forma:

$ docker run --name my-publication_stats -e ELASTICSEARCH=my_eshost:27017 -p 8000:8000 -p 11620:11620 -d my-publication_stats

Para executar os processamentos disponíveis em console scripts, executar:

Carga de Licenças de uso:

$ docker exec -i -t publication_stats publicationstats_loaddata --help
