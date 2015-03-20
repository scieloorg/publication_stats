# coding: utf-8
import logging
import sys

import elasticsearch
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
        hosts = ['esa.scielo.org', 'esb.scielo.org']

    return Stats(hosts)

class ServerError(Exception):

    def __init__(self, value):
        self.message = 'Server Error: %s' % str(value)

    def __str__(self):
        return repr(self.message)

class Stats(Elasticsearch):

    def _query_dispatcher(self, *args, **kwargs):

        try:
            data = self.search(*args, **kwargs)
        except elasticsearch.SerializationError:
            logging.error('ElasticSearch SerializationError')
            raise ServerError()
        except elasticsearch.TransportError as e:
            logging.error('ElasticSearch TransportError: %s' % e.error)
            raise ServerError()
        except elasticsearch.ConnectionError as e:
            logging.error('ElasticSearch ConnectionError: %s' % e.error)
            raise ServerError()
        except:
            logging.error("Unexpected error: %s" % sys.exc_info()[0])
            raise ServerError()

        return data

    def publication_search(self, parameters):

        parameters['index'] = 'publication'
        query_result = self._query_dispatcher(**parameters)

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

        query_result = self._query_dispatcher(
            index='publication',
            doc_type=doc_type,
            search_type='count',
            body=body
        )

        response = {item['key']:item['doc_count'] for item in query_result['aggregations'][facet]['buckets']}

        return response