.. _journal_statuses:

journal_statuses
----------------

Lista a contagem de periódicos por status de publicação.

**definição**

list<:ref:`aggs`> journal_statuses(1: optional map<string,string> :ref:`filters`) throws (1:ValueError value_err, 2:ServerError server_err)

Resumo
``````

Esta função deve retornar uma lista de structs :ref:`aggs`, podendo através do
parâmetro opcional :ref:`filters` restringir o escopo do resultado.

Exemplo de resultado::

  [
    aggs(count=1142, key=u'current'),
    aggs(count=8, key=u'inprogress'),
    aggs(count=69, key=u'deceased'),
    aggs(count=92, key=u'suspended'),
    ...
  ]

Casos de uso
````````````

* Uso geral de coleta de indicadores de publicação.
