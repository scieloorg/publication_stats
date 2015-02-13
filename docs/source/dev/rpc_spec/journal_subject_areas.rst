.. _journal_subject_areas:

journal_subject_areas
---------------------

Lista a contagem de periódicos por área temática. 

**definição**

list<:ref:`aggs`> journal_subject_areas(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=124, key=u'Agricultural Sciences'),
    aggs(count=415, key=u'Health Sciences'),
    aggs(count=259, key=u'Applied Social Sciences'),
    aggs(count=380, key=u'Human Sciences'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
