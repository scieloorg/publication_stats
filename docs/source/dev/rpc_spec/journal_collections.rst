.. _journal_collections:

journal_collections
---------------------

Lista a contagem de periódicos por coleção.

**definição**

list<:ref:`aggs`> journal_collections(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=342, key=u'scl'),
    aggs(count=57, key=u'esp'),
    aggs(count=52, key=u'sza'),
    aggs(count=106, key=u'chl'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
