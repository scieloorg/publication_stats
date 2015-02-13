.. _document_subject_areas:

document_sunject_areas
----------------------

Lista a contagem de documentos por area temática.

**definição**

list<:ref:`aggs`> document_sunject_areas(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=76498, key=u'Agricultural Sciences'),
    aggs(count=270763, key=u'Health Sciences'),
    aggs(count=49011, key=u'Applied Social Sciences'),
    aggs(count=98085, key=u'Human Sciences'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
