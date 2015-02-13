.. _document_affiliation_countries:

document_affiliation_countries
------------------------------

Lista a contagem de documentos por país de afiliação dos autores.

**definição**

list<:ref:`aggs`> document_affiliation_countries(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=136, key=u'BD'),
    aggs(count=690, key=u'BE'),
    aggs(count=25, key=u'BF'),
    aggs(count=79, key=u'BG'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
