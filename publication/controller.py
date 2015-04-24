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

def construct_aggs(aggs, size=0):
    """
    Construct the ElasticSearch aggretions query according to a list of
    parameters that must be aggregated.
    """

    data = {}
    point = None
    def join(field, point=None):
        default = {
            field: {
                "terms": {
                    "field": field,
                    "size": 0
                }
            }
        }

        if point:
            point.setdefault('aggs', default)
            return point['aggs'][field]
        else:
            data.setdefault('aggs', default)
            return data['aggs'][field]

    for item in aggs:
        point = join(item, point=point)

    return data


def stats(*args, **kwargs):

    if not 'hosts' in kwargs:
        kwargs['hosts'] = ['esa.scielo.org', 'esb.scielo.org']

    return Stats(*args, **kwargs)

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

    def publication_stats(self, doc_type, aggs, filters=None):

        if not aggs:
            raise ValueError(
                u'Aggregation not allowed, %s, expected %s' % (
                    str(aggs),
                    str(ALLOWED_DOC_TYPES_N_FACETS[doc_type])
                )
            )

        if not doc_type in ALLOWED_DOC_TYPES_N_FACETS.keys():
            raise ValueError(
                u'DocumentType not allowed, %s, expected %s' % (
                    doc_type,
                    str(ALLOWED_DOC_TYPES_N_FACETS.keys())
                )
            )
        
        for agg in aggs:
            if not agg in ALLOWED_DOC_TYPES_N_FACETS[doc_type]:
                raise ValueError(
                    u'Aggregation not allowed, %s, expected %s' % (
                        aggs,
                        str(ALLOWED_DOC_TYPES_N_FACETS[doc_type])
                    )
                )

        body = {
            "query": {
                "match_all": {}
            }
        }

        body.update(construct_aggs(aggs))

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

        response = query_result['aggregations']

        return response