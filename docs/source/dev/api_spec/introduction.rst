Introdução
==========

Esta API possui 2 endpoints para recuperação de estatísticas de publicação, sendo
um relacionado a estatísticas de periódicos e outro relacionado a relacionado
a estatísticas de documentos.

API URL: http://publication.scielo.org

API Version: v1

Periódicos
----------

Retorna estatísticas de publicação relacionadas aos periódicos publicados na
Rede SciELO.

Endpoint::

/api/b1/journals

Parâmetros:

+--------------+-----------------------------+-----------------------------+
| Paremetro    | Descrição                   | Obrigatório                 |
+==============+=============================+=============================+
| aggs         | Agregação dos Indicaores    | Yes                         |
+--------------+-----------------------------+-----------------------------+
| callback     | JSONP callback method       | No                          |
+--------------+-----------------------------+-----------------------------+
| collection   | collection acronym          | No                          |
+--------------+-----------------------------+-----------------------------+
| issn         | journal issn                | No                          |
+--------------+-----------------------------+-----------------------------+
| subject_area | subject area                | No                          |
+--------------+-----------------------------+-----------------------------+


.. HINT::

    Os valores aceitos para o atributo `aggs` são: ['collection',
    'subject_areas', 'issn', 'status', 'included_at_year']

.. HINT::

    Os parametros opcionais ['collection', 'issn', 'sunject_area'] com exceção
    do `callback` são todos utilizados para realizar filtragem de registros.

**Exemplo 1:**

Distribuição número de periódicos por área temática na Rede SciELO.

Query::

    /api/v1/journals?aggs=subject_areas

Response::

    {
        "subject_areas": {
            "buckets": [
                {
                    "key": "Health Sciences", 
                    "doc_count": 436
                }, 
                {
                    "key": "Human Sciences", 
                    "doc_count": 403
                }, 
                {
                    "key": "Applied Social Sciences", 
                    "doc_count": 281
                }, 
                {
                    "key": "Biological Sciences", 
                    "doc_count": 164
                }, 
                {
                    "key": "Agricultural Sciences", 
                    "doc_count": 132
                }, 
                {
                    "key": "Exact and Earth Sciences", 
                    "doc_count": 104
                }, 
                {
                    "key": "Engineering", 
                    "doc_count": 101
                }, 
                {
                    "key": "Linguistics, Letters and Arts", 
                    "doc_count": 56
                }, 
                {
                    "key": "Social Sciences", 
                    "doc_count": 3
                }, 
                {
                    "key": "Ciencias", 
                    "doc_count": 2
                }, 
                {
                    "key": "Ciencias exactas y de la tierra", 
                    "doc_count": 2
                }, 
                {
                    "key": "Mathematics", 
                    "doc_count": 1
                }
            ], 
            "sum_other_doc_count": 0, 
            "doc_count_error_upper_bound": 0
        }
    }

Documentos
----------

Retorna estatísticas de publicação relacionadas aos documentos publicados na
Rede SciELO.

Endpoint::

/api/b1/documents

Parâmetros:

+---------------------+-----------------------------+-----------------------------+
| Paremetro           | Descrição                   | Obrigatório                 |
+=====================+=============================+=============================+
| aggs                | Agregação dos Indicaores    | Yes                         |
+---------------------+-----------------------------+-----------------------------+
| callback            | JSONP callback method       | No                          |
+---------------------+-----------------------------+-----------------------------+
| collection          | collection acronym          | No                          |
+---------------------+-----------------------------+-----------------------------+
| issn                | journal issn                | No                          |
+---------------------+-----------------------------+-----------------------------+
| subject_area        | subject area                | No                          |
+---------------------+-----------------------------+-----------------------------+
| affiliation_country | ISO-6391 - 2 letras         | No                          |
+---------------------+-----------------------------+-----------------------------+
| publication_year    | Ano de publicação - YYYY    | No                          |
+---------------------+-----------------------------+-----------------------------+
| document_type       | Tipo de documento           | No                          |
+---------------------+-----------------------------+-----------------------------+
| language            | ISO-6391 - 2 letras         | No                          |
+---------------------+-----------------------------+-----------------------------+


.. HINT::

    Os valores aceitos para o atributo `aggs` são: ['collection',
    'subject_areas', 'languages', 'aff_countries', 'publication_year',
    'document_type', 'issn']

.. HINT::

    Os parametros opcionais ['collection', 'issn', 'subject_area',
    'affiliation_country', 'publication_year', 'document_type', 'language'] com
    exceção do `callback` são todos utilizados para realizar filtragem de
    registros.

**Exemplo 1:**

Distribuição de documentos por ano de publicação e área temática na coleção
SciELO Brasil.

Query::

    /api/v1/documents?aggs=publication_year,subject_areas&collection=scl

Response::

    {
        "publication_year": {
            "buckets": [
                {
                    "subject_areas": {
                        "buckets": [
                            {
                                "key": "Health Sciences", 
                                "doc_count": 10069
                            }, 
                            {
                                "key": "Agricultural Sciences", 
                                "doc_count": 4372
                            }, 
                            {
                                "key": "Human Sciences", 
                                "doc_count": 4184
                            }, 
                            {
                                "key": "Biological Sciences", 
                                "doc_count": 2803
                            }, 
                            {
                                "key": "Engineering", 
                                "doc_count": 1370
                            }, 
                            {
                                "key": "Exact and Earth Sciences", 
                                "doc_count": 1305
                            }, 
                            {
                                "key": "Applied Social Sciences", 
                                "doc_count": 1302
                            }, 
                            {
                                "key": "Linguistics, Letters and Arts", 
                                "doc_count": 373
                            }
                        ], 
                        "sum_other_doc_count": 0, 
                        "doc_count_error_upper_bound": 0
                    }, 
                    "key": "2012", 
                    "doc_count": 22385
                }, 
                {
                    "subject_areas": {
                        "buckets": [
                            {
                                "key": "Health Sciences", 
                                "doc_count": 10358
                            }, 
                            {
                                "key": "Agricultural Sciences", 
                                "doc_count": 4519
                            }, 
                            {
                                "key": "Human Sciences", 
                                "doc_count": 3696
                            }, 
                            {
                                "key": "Biological Sciences", 
                                "doc_count": 2896
                            }, 
                            {
                                "key": "Applied Social Sciences", 
                                "doc_count": 1208
                            }, 
                            {
                                "key": "Exact and Earth Sciences", 
                                "doc_count": 1206
                            }, 
                            {
                                "key": "Engineering", 
                                "doc_count": 1165
                            }, 
                            {
                                "key": "Linguistics, Letters and Arts", 
                                "doc_count": 282
                            }
                        ], 
                        "sum_other_doc_count": 0, 
                        "doc_count_error_upper_bound": 0
                    }, 
                    "key": "2011", 
                    "doc_count": 22128
                }
            ]
        }
    }

**Exemplo 2:**

Distribuição de idioma dos documentos por ano de publicação para o periódico de
issn **0103-6440**.

Query::

    /api/v1/documents?aggs=languages,publication_year&issn=0103-6440

Response::

    {
        "languages": {
            "buckets": [
                {
                    "publication_year": {
                        "buckets": [
                            {
                                "key": "2012", 
                                "doc_count": 118
                            }, 
                            {
                                "key": "2013", 
                                "doc_count": 114
                            }, 
                            {
                                "key": "2014", 
                                "doc_count": 99
                            }, 
                            {
                                "key": "2010", 
                                "doc_count": 91
                            }, 
                            {
                                "key": "2011", 
                                "doc_count": 89
                            }, 
                            {
                                "key": "2009", 
                                "doc_count": 75
                            }, 
                            {
                                "key": "2006", 
                                "doc_count": 67
                            }, 
                            {
                                "key": "2007", 
                                "doc_count": 65
                            }, 
                            {
                                "key": "2008", 
                                "doc_count": 60
                            }, 
                            {
                                "key": "2004", 
                                "doc_count": 45
                            }, 
                            {
                                "key": "2005", 
                                "doc_count": 44
                            }, 
                            {
                                "key": "2003", 
                                "doc_count": 41
                            }, 
                            {
                                "key": "2015", 
                                "doc_count": 35
                            }, 
                            {
                                "key": "2002", 
                                "doc_count": 27
                            }
                        ], 
                        "sum_other_doc_count": 0, 
                        "doc_count_error_upper_bound": 0
                    }, 
                    "key": "en", 
                    "doc_count": 970
                }, 
                {
                    "publication_year": {
                        "buckets": [
                            {
                                "key": "2010", 
                                "doc_count": 6
                            }, 
                            {
                                "key": "2011", 
                                "doc_count": 5
                            }, 
                            {
                                "key": "2009", 
                                "doc_count": 2
                            }
                        ], 
                        "sum_other_doc_count": 0, 
                        "doc_count_error_upper_bound": 0
                    }, 
                    "key": "pt", 
                    "doc_count": 13
                }
            ], 
            "sum_other_doc_count": 0, 
            "doc_count_error_upper_bound": 0
        }
    }
