.. _document_publication_years:

document_publication_years
--------------------------

Lista a contagem de periódicos por ano de inclusão do periódico na coleção.

**definição**

list<:ref:`aggs`> document_publication_years(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=122, key=u'1948'),
    aggs(count=118, key=u'1949'),
    aggs(count=108, key=u'1942'),
    aggs(count=158, key=u'1943'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
