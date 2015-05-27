Serviço de extração de estatísticas de publicação
=================================================

Este serviço fornece duas modalidades de extração de indicadores de publicação
das coleções da Rede SciELO.

* servidor RPC com um conjunto de endpoints para recuperação de indicadores de publicação das coleções, periódicos e documentos da Rede SciELO.

* API pública com um conjunto de endpoints para recuperação de indicadores de publicação das coleções, periódicos e documentos da Rede SciELO.

Os indicaores estatísticos estão relacionados aos seguuintes aspectos:

**Periódicos**

 * Coleções
 * Áreas temáticas
 * Status do Periódico na rede SciELO
 * Data de inclusão na rede ScIELO

**Documentos**

 * Coleções
 * Áreas temáticas
 * Idiomas disponíveis
 * País de afiliação
 * Ano de publicação
 * Tipos de documentos
 * Periódico (ISSN, título)


Endpoints da API
================

.. toctree::
   :maxdepth: 2

   dev/api_spec/introduction

Exemplo de cliente
------------------

.. toctree::
   :maxdepth: 1

   dev/api_client_sample


RPC Endpoints
=============

.. toctree::
   :maxdepth: 2

   dev/rpc_spec/journal_subject_areas
   dev/rpc_spec/journal_collections
   dev/rpc_spec/journal_statuses
   dev/rpc_spec/journal_inclusion_years
   dev/rpc_spec/document_subject_areas
   dev/rpc_spec/document_collections
   dev/rpc_spec/document_publication_years
   dev/rpc_spec/document_languages
   dev/rpc_spec/document_affiliation_countries
   dev/rpc_spec/document_types
   dev/rpc_spec/search
   

Exemplo de cliente
------------------

.. toctree::
   :maxdepth: 1

   dev/rpc_client_sample

Structs
-------

.. toctree::
   :maxdepth: 2

   dev/rpc_spec/structs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`