# coding: utf-8
import os
import thriftpy
import json

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