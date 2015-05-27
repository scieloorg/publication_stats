Exemplo de Cliente de API
=========================

python::

    # coding: utf-8
    import os
    import json

    import thriftpy

    publication_stats_thrift = thriftpy.load(
        os.path.dirname(__file__)+'/publication_stats.thrift',
        module_name='publication_stats_thrift'
    )

    from thriftpy.rpc import make_client

    client = make_client(
        publication_stats_thrift.PublicationStats,
        '127.0.0.1',
        11620
    )

    # Distribuição por Ano de Publicação
    print client.document_publication_years()


    # Distribuição por Ano de Publicação filtrado por coleção.
    print client.document_publication_years({'collection': 'scl'})

    # Distribuição por Ano de Publicação filtrado por coleção e tipo de documento.
    print client.document_publication_years({'collection': 'scl', 'document_type': 'research-article'})

    # Pesquisa livre
    body = {
      "query": {
        "match": {
          "collection": "scl"
        }
      },
      "aggs": {
        "languages": {
          "terms": {
            "field": "languages"
          }
        }
      }
    }

    parameters = [
        publication_stats_thrift.kwargs('search_type', 'count')
    ]

    print json.loads(client.search('article', json.dumps(body), parameters))

