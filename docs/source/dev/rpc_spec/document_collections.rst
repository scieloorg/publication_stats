.. _document_collections:

document_collections
---------------------

Lista a contagem de documentos por coleção.

**definição**

list<:ref:`aggs`> document_collections(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=278413,key=u'scl'),
    aggs(count=27426, key=u'esp'),
    aggs(count=11371, key=u'sza'),
    aggs(count=45834, key=u'chl'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
