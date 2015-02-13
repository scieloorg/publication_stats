.. _journal_inclusion_years:

journal_inclusion_years
-----------------------

Lista a contagem de periódicos por ano de inclusão do periódico na coleção.

**definição**

list<:ref:`aggs`> journal_inclusion_years(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=9, key=u'1997'),
    aggs(count=18, key=u'1999'),
    aggs(count=29, key=u'1998'),
    aggs(count=71, key=u'2002'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
