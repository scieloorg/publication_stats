.. _document_languages:

document_languages
------------------

Lista a contagem de documentos por idioma de publicação.

**definição**

list<:ref:`aggs`> document_languages(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=159964, key=u'en'),
    aggs(count=1, key=u'gr'),
    aggs(count=864, key=u'af'),
    aggs(count=2, key=u'ca'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
