# coding: utf-8
import logging
from datetime import datetime, timedelta
import argparse
import os
import sys

import requests
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.client import IndicesClient

from publication import utils
from thrift import clients
from processing import choices

logger = logging.getLogger(__name__)

config = utils.Configuration.from_env()
settings = dict(config.items())

FROM = datetime.now() - timedelta(days=30)
FROM = FROM.isoformat()[:10]
ES = Elasticsearch(settings['app:main']['elasticsearch'], timeout=360)


def articlemeta(address=None):
    """
    address: 127.0.0.1:11720
    """
    address = address or settings['app:main'].get(
        'articlemeta', '127.0.0.1:11720')

    host = address.split(':')[0]
    try:
        port = int(address.split(':')[1])
    except:
        port = 11720

    return clients.ArticleMeta(host, port)


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)

    return logger


def fmt_journal(document):
    data = {}

    data['id'] = '_'.join([document.collection_acronym, document.scielo_issn])
    data['issn'] = document.scielo_issn
    data['collection'] = document.collection_acronym
    data['subject_areas'] = document.subject_areas
    data['included_at_year'] = document.creation_date[0:4]
    data['status'] = document.current_status
    data['title'] = document.title
    permission = document.permissions or {'id': 'undefined'}
    data['license'] = permission.get('id' or 'undefined')

    return data


def country(country):

    code = country.upper()

    if code in choices.ISO_3166_COUNTRY_CODE:
        return code

    if code in choices.ISO_3166_COUNTRY_NAME_AS_KEY:
        return choices.ISO_3166_COUNTRY_NAME_AS_KEY[code]

    return 'undefined'


def state(state, country_code):

    code = '-'.join([country_code, state])
    code = code.upper()

    if code in choices.ISO_3166_DIVISION_CODE:
        return code

    return choices.ISO_3166_DIVISION_NAME_AS_KEY.get(state.upper(), 'undefined')


def pages(first, last):

    try:
        pages = int(last)-int(first)
    except:
        pages = 0

    if pages >= 0:
        return pages
    else:
        return 0


def acceptancedelta(received, accepted):

    try:
        rec = datetime.strptime(received, '%Y-%m-%d')
    except:
        return None

    try:
        acc = datetime.strptime(accepted, '%Y-%m-%d')
    except:
        return None

    delta = acc-rec

    days = delta.days

    if days >= 0:
        return days


def fmt_document(document):
    data = {}

    data['id'] = '_'.join([document.collection_acronym, document.publisher_id])
    data['pid'] = document.publisher_id
    data['issn'] = document.journal.scielo_issn
    data['journal_title'] = document.journal.title
    data['issue'] = '_'.join([document.collection_acronym, document.publisher_id[0:18]])
    data['issue_type'] = document.issue.type if document.issue else 'undefined'
    data['creation_year'] = document.creation_date[0:4]
    data['creation_date'] = document.creation_date
    data['processing_year'] = document.processing_date[0:4]
    data['processing_date'] = document.processing_date
    data['publication_date'] = document.publication_date
    data['publication_year'] = document.publication_date[0:4]
    subject_areas = document.journal.subject_areas or ['undefined']
    data['subject_areas'] = [i for i in subject_areas]
    wos_subject_areas = document.journal.wos_subject_areas or ['undefined']
    data['wos_subject_areas'] = wos_subject_areas
    data['collection'] = document.collection_acronym
    data['document_type'] = document.document_type
    pgs = pages(document.start_page, document.end_page)
    data['pages'] = pgs
    data['languages'] = [i.lower() for i in list(set(document.languages()+[document.original_language() or 'undefined']))]
    data['aff_countries'] = ['undefined']
    data['aff_states_name'] = ['undefined']
    if document.mixed_affiliations:
        data['aff_countries'] = list(set([country(aff.get('country', 'undefined')) for aff in document.mixed_affiliations]))
        data['aff_states_code'] = list(set([state(aff.get('state', 'undefined'), country(aff.get('country', 'undefined'))) for aff in document.mixed_affiliations]))
        data['aff_names'] = list(set([aff['institution'] for aff in document.mixed_affiliations if aff.get('institution', None)]))
        data['aff_names_analyzed'] = data['aff_names']
        data['aff_names_cleaned'] = list(set([utils.cleanup_string(i) for i in data['aff_names']]))
        data['aff_states_name'] = list(set([choices.ISO_3166_DIVISION_CODE.get(i, 'undefied') for i in data['aff_states_code']]))
    keywords = []
    kws = document.keywords() or {}
    if kws:
        for item in kws.values():
            keywords += item
        data['keywords'] = keywords
        data['keywords_analyzed'] = keywords
    data['citations'] = len(document.citations or [])
    data['authors'] = len(document.authors or [])
    permission = document.permissions or {'id': 'undefined'}
    data['license'] = permission.get('id' or 'undefined')
    if document.doi:
        data['doi'] = document.doi
        data['doi_prefix'] = document.doi.split('/')[0]

    delta = acceptancedelta(document.receive_date, document.acceptance_date)
    if delta:
        data['acceptance_delta'] = delta

    return data


def documents(endpoint, collection=None, issns=None, fmt=None, from_date=FROM, identifiers=False):

    allowed_endpoints = ['journal', 'article']

    if not endpoint in allowed_endpoints:
        raise TypeError('Invalid endpoint, expected one of: %s' % str(allowed_endpoints))

    for issn in issns:
        if endpoint == 'article':
            if identifiers:
                itens = articlemeta().documents(collection=collection, issn=issn, from_date=from_date)
            else:
                itens = articlemeta().documents_history(collection=collection, from_date=from_date)
        elif endpoint == 'journal':
            if identifiers:
                itens = articlemeta().journals()
            else:
                itens = articlemeta().journals_history(collection=collection, from_date=from_date)

        for item in itens:

            if not identifiers:  # mode history changes
                history = item[0]
                if history.event == 'delete':
                    delete_params = {'collection': history.collection}
                    if endpoint == 'article':
                        delete_params['code'] = history.code or ''
                    elif endpoint == 'journal':
                        delete_params['issn'] = history.code[0] or ''
                    code = delete_params.get('code', delete_params.get('issn', ''))
                    if not code:
                        continue
                    delete_params['id'] = '_'.join([history.collection, code])
                    yield ('delete', delete_params)
                doc_ret = item[1]
            else:
                doc_ret = item

            yield ('add', fmt(doc_ret))


def run(doc_type, index='publication', collection=None, issns=None, from_date=FROM, identifiers=False):

    journal_settings_mappings = {
        "mappings": {
            "journal": {
                "properties": {
                    "collection": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "id": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "issn": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "subject_areas": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "title": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "included_at_year": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "status": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "license": {
                        "type": "string",
                        "index": "not_analyzed"
                    }
                }
            },
            "citation": {
                "properties": {
                    "collection": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "id": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "pid": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "citation_type": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "publication_year": {
                        "type": "string",
                        "index": "not_analyzed"
                    }
                }
            },
            "article": {
                "properties": {
                    "id": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "pid": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "issn": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "issue": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "subject_areas": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "wos_subject_areas": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "collection": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "languages": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "aff_countries": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "aff_names": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "aff_names_cleaned": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "aff_names_analyzed": {
                        "type": "string"
                    },
                    "aff_states_code": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "aff_states_name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "keywords": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "keywords_analyzed": {
                        "type": "string"
                    },
                    "document_type": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "journal_title": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "license": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "creation_date": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "creation_year": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "processing_year": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "processing_date": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "publication_year": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "publication_date": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "doi": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "doi_prefix": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "issue_type": {
                        "type": "string",
                        "index": "not_analyzed"
                    }
                }
            }
        }
    }

    try:
        ES.indices.create(index=index, body=journal_settings_mappings)
    except:
        logger.debug('Index already available')

    if doc_type == 'journal':
        endpoint = 'journal'
        fmt = fmt_journal
    elif doc_type == 'article':
        endpoint = 'article'
        fmt = fmt_document
    else:
        logger.error('Invalid doc_type')
        exit()

    for event, document in documents(endpoint, collection=collection, issns=issns, fmt=fmt, from_date=from_date, identifiers=identifiers):
        if event == 'delete':
            logger.debug('removing document %s from index %s' % (document['id'], doc_type))
            try:
                ES.delete(index=index, doc_type=doc_type, id=document['id'])
            except NotFoundError:
                logger.debug('Record already removed: %s' % document['id'])
            except:
                logger.error('Unexpected error: %s' % sys.exc_info()[0])

        else:  # event would be ['add', 'update']
            logger.debug('loading document %s into index %s' % (document['id'], doc_type))
            ES.index(
                index=index,
                doc_type=doc_type,
                id=document['id'],
                body=document
            )


def main():

    parser = argparse.ArgumentParser(
        description="Load SciELO Network data no analytics production"
    )

    parser.add_argument(
        'issns',
        nargs='*',
        help='ISSN\'s separated by spaces'
    )

    parser.add_argument(
        '--collection',
        '-c',
        help='Collection Acronym'
    )

    parser.add_argument(
        '--from_date',
        '-f',
        default=FROM,
        help='ISO date like 2013-12-31'
    )

    parser.add_argument(
        '--index',
        '-x',
        default='publication',
        help='Define the index to populate.'
    )

    parser.add_argument(
        '--identifiers',
        '-i',
        action='store_true',
        help='Define the identifiers endpoint to retrieve the document and journal codes. If not given the enpoint used will be the history. When using history the processing will also remove records from the index.'
    )

    parser.add_argument(
        '--logging_file',
        '-o',
        help='Full path to the log file'
    )

    parser.add_argument(
        '--doc_type',
        '-d',
        choices=['article', 'journal'],
        help='Document type that will be updated'
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()

    _config_logging(args.logging_level, args.logging_file)

    issns = None
    if len(args.issns) > 0:
        issns = utils.ckeck_given_issns(args.issns)

    run(args.doc_type, index=args.index, collection=args.collection, issns=issns or [None], from_date=args.from_date, identifiers=args.identifiers)
