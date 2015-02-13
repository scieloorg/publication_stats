.. _document_types:

document_types
--------------

Lista a contagem de documentos por tipo de documento.

**definição**

list<:ref:`aggs`> document_types(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=432613, key=u'research-article'),
    aggs(count=7457, key=u'article-commentary'),
    aggs(count=9592, key=u'brief-report'),
    aggs(count=4802, key=u'abstract'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
