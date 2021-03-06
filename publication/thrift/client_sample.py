# coding: utf-8
import os
import thriftpy
import json

from thriftpy.rpc import make_client

publication_stats_thrift = thriftpy.load(
    os.path.dirname(__file__)+'/publication_stats.thrift',
    module_name='publication_stats_thrift'
)

if __name__ == '__main__':

    client = make_client(
        publication_stats_thrift.PublicationStats,
        'publication.scielo.org',
        11620
    )

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

    print(json.loads(client.search('article', json.dumps(body), parameters)))
