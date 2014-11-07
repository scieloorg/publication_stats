# coding: utf-8
import logging

import requests

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from xylose.scielodocument import Article, Journal

import choices

ARTICLEMETA = "http://articlemeta.scielo.org/api/v1"
ISO_3166_COUNTRY_AS_KEY = {value: key for key, value in choices.ISO_3166.items()}

ES = Elasticsearch()

def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logging_config = {
        'level': allowed_levels.get(logging_level, 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }

    if logging_file:
        logging_config['filename'] = logging_file

    logging.basicConfig(**logging_config)

def do_request(url, params):

    response = requests.get(url, params=params).json()

    return response


def fmt_document(document):
    return document

def fmt_journal(document):
    data = {}

    data['id'] = document.scielo_issn
    data['issn'] = document.scielo_issn
    data['collection'] = document.collection_acronym
    data['subject_areas'] = document.subject_areas
    data['title'] = document.title

    return data

def country(country):
    if country in choices.ISO_3166:
        return country
    if country in ISO_3166_COUNTRY_AS_KEY:
        return ISO_3166_COUNTRY_AS_KEY[country]
    return 'undefined'

def pages(first, last):

    try:
        pages = last-first
    except:
        pages = None

    return pages

def fmt_article(document, collection='BR'):
    data = {}

    data['id'] = '_'.join([document.collection_acronym, document.publisher_id])
    data['pid'] = document.publisher_id
    data['issn'] = document.journal.scielo_issn
    data['journal_title'] = document.journal.title
    data['issue'] = '_'.join([document.collection_acronym, document.publisher_id[0:18]])
    data['publication_date'] = document.publication_date
    data['publication_year'] = document.publication_date[0:4]
    data['subject_areas'] = [i for i in document.journal.subject_areas]
    data['collection'] = document.collection_acronym
    data['document_type'] = document.document_type
    pgs = pages(document.start_page, document.end_page)
    if pages:
        data['pages'] = pgs
    data['languages'] = list(set([i for i in document.languages().keys()]+[document.original_language() or 'undefined']))
    data['aff_countries'] = ['undefined']
    if document.mixed_affiliations:
        data['aff_countries'] = list(set([country(aff.get('country', 'undefined')) for aff in document.mixed_affiliations]))
    data['citations'] = len(document.citations or [])

    return data

def documents(endpoint, fmt=None):

    allowed_endpoints = ['journal', 'article']

    if not endpoint in allowed_endpoints:
        raise TypeError('Invalid endpoint, expected one of: %s' % str(allowed_endpoints))

    params = {'offset': 0}

    if endpoint == 'article':
        xylose_model = Article
    elif endpoint == 'journal':
        xylose_model = Journal

    while True:
        identifiers = do_request(
            '{0}/{1}/identifiers'.format(ARTICLEMETA, endpoint),
            params
        )

        logging.debug('offset %s' % str(params['offset']))

        logging.debug('len identifiers %s' % str(len(identifiers['objects'])))

        if len(identifiers['objects']) == 0:
            raise StopIteration

        for identifier in identifiers['objects']:
            dparams = {
                'collection': identifier['collection']
            }

            if endpoint == 'article':
                dparams['code'] = identifier['code']
            elif endpoint == 'journal':
                dparams['issn'] = identifier['code'][0]

            document = do_request(
                '{0}/{1}'.format(ARTICLEMETA, endpoint), dparams
            )

            if isinstance(document, dict):
                doc_ret = document
            elif isinstance(document, list):
                doc_ret = document[0]

            yield fmt(xylose_model(doc_ret))

        params['offset'] += 1000

if __name__ == '__main__':

    _config_logging(logging_level='DEBUG')

    journal_settings_mappings = {      
        "mappings": {
            "journal": {
                "properties": {
                    "collection": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "id": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "issn": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "subject_areas": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "title": {
                        "type": "string",
                        "index" : "not_analyzed"
                    }
                }
            },
            "article": {
                "properties": {
                    "id": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "pid": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "issn": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "issue": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "subject_areas": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "collection": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "languages": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "aff_countries": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "document_type": {
                        "type": "string",
                        "index" : "not_analyzed"
                    },
                    "journal_title": {
                        "type": "string",
                        "index" : "not_analyzed"
                    }
                }
            }
        }
    }

    try:
        ES.indices.create(index='production', body=journal_settings_mappings)
    except:
        logging.debug('Index already available')

    for document in documents('journal', fmt_journal):
        logging.debug('loading document %s into index %s' % (document['id'], 'journal'))
        ES.index(
            index='production',
            doc_type='journal',
            id=document['id'],
            body=document
        )

    for document in documents('article', fmt_article):
        logging.debug('loading document %s into index %s' % (document['id'], 'article'))
        ES.index(
            index='production',
            doc_type='article',
            id=document['id'],
            body=document
        )