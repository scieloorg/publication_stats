.. _search:

search
------

Este serviço permite realizar buscas livres no elasticsearch.

**definição**

string search(1:string doc_type, 2: string body, 3: optional list<:ref:`kwargs`> parameters) throws (1:ValueError value_err, 2:ServerError server_err)

A lista de parametros aceitos la lista de ::ref`kwargs` esta disponível em:

https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.search

Resumo
``````

Esta função deve retornar uma sring "json" com o resultado da pesquisa realizada.

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
