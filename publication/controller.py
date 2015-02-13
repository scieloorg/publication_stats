# coding: utf-8
import logging

from elasticsearch import ElasticsearchException
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from xylose.scielodocument import Article, Journal

ALLOWED_DOC_TYPES_N_FACETS = {
    'journal': [
        'collection',
        'subject_areas',
        'issn',
        'status',
        'included_at_year',
    ],
    'article': [
        'collection',
        'subject_areas',
        'languages',
        'aff_countries',
        'publication_year',
        'document_type',
        'issn',
    ]
}

def stats(hosts=None):

    if not hosts:
        hosts = ['homolog.esa.scielo.org', 'homolog.esb.scielo.org']

    return Stats(hosts)

class IndexError(Exception):

    def __init__(self, value):
        self.value = value
        self.message = value
    
    def __str__(self):
        return repr(self.value)

class Stats(Elasticsearch):

    def publication_search(self, *args, **kwargs):

        kwargs['index'] = 'publication'

        try:
            query_result = self.search(*args, **kwargs)
        except ElasticsearchException as e:
            logging.error('ElasticSearch Error: %s' % e.message)
            raise

        return query_result

    def publication_stats(self, doc_type, facet, filters=None, aggs=None):

        if not doc_type in ALLOWED_DOC_TYPES_N_FACETS.keys():
            raise ValueError(
                u'DocumentType not allowed, %s, expected %s' % (
                    doc_type,
                    str(ALLOWED_DOC_TYPES_N_FACETS.keys())
                )
            )

        if not facet in ALLOWED_DOC_TYPES_N_FACETS[doc_type]:
            raise ValueError(
                u'Facet not allowed, %s, expected %s' % (
                    facet,
                    str(ALLOWED_DOC_TYPES_N_FACETS[doc_type])
                )
            )

        if aggs and not aggs in ALLOWED_DOC_TYPES_N_FACETS[doc_type]:
            raise ValueError(
                u'Aggregation not allowed, %s, expected %s' % (
                    aggs,
                    str(ALLOWED_DOC_TYPES_N_FACETS[doc_type])
                )
            )

        body = {
            "query": {
                "match_all": {}
            },
            "aggs": {
                facet: {
                    "terms": {
                        "field": facet,
                        "size": 0
                    }
                }
            }
        }

        if filters:
            must_terms = []
            for param, value in filters.items():
                if not param in ALLOWED_DOC_TYPES_N_FACETS[doc_type]:
                    raise ValueError(
                        u'Filter not allowed, %s expected %s' % (
                            param,
                            str(ALLOWED_DOC_TYPES_N_FACETS[doc_type])
                        )
                    )
                must_terms.append({'term': {param:value}})

            body['query'] = {
                "bool": {
                    "must": must_terms
                }
            }

        query_result = self.search(
            index='production',
            doc_type=doc_type,
            search_type='count',
            body=body
        )

        response = {item['key']:item['doc_count'] for item in query_result['aggregations'][facet]['buckets']}

        return response