.. _aggs:

``aggs``
========

..block::

    struct aggs {
        1: string key,
        2: i32 count,
    }


.. _kwargs:

``kwargs``
==========

..block::

    struct kwargs {
        1: string key,
        2: value value,
    }

Esta ``struct`` é utilizada pelo serviço :ref:`search`, para transportar 
parametros de configuração de uma pesquisa no elasticsearch.


https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.search


.. _filters:

``filters``
===========

definição::

    struct filters {
        1: string param,
        2: string value
    }


Esta ``struct`` quando aceita por uma função, permite realizar filtros no escopo
da pesquisa. Os filtros permitidos podem variar de acordo com a função
utilizada.

Para funções de recuperação de indicadores de periódico (journals), os metodos
aceitos são:

    * collection
    * subject_areas
    * issn
    * status
    * included_at_year

Para funções de recuperação de indicadores de documentos (documents), os metodos
aceitos são:

    * collection
    * subject_areas
    * languages
    * aff_countries
    * publication_year
    * document_type
    * issn
