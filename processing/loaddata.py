# coding: utf-8
import logging
import logging.config
from datetime import datetime, timedelta
import argparse
import os
import sys

from elasticsearch import Elasticsearch, NotFoundError, RequestError

from publication import utils
from articlemeta import client
from processing import choices

logger = logging.getLogger(__name__)

SENTRY_HANDLER = os.environ.get('SENTRY_HANDLER', None)
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'DEBUG')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'console': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%H:%M:%S',
            },
        },
    'handlers': {
        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'console'
            }
        },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
            'propagate': False,
            },
        'processing.loaddata': {
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
    }
}

if SENTRY_HANDLER:
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.handlers.logging.SentryHandler',
        'dsn': SENTRY_HANDLER,
    }
    LOGGING['loggers']['']['handlers'].append('sentry')


FROM = datetime.now() - timedelta(days=30)
FROM = FROM.isoformat()[:10]
UNTIL = datetime.now().isoformat()[:10]

ES = Elasticsearch(
    os.environ.get('ELASTICSEARCH', '127.0.0.1:9200'), timeout=360)


def articlemeta(address=None):
    """
    address: 127.0.0.1:11720
    """
    address = address or os.environ.get(
        'ARTICLEMETA_THRIFTSERVER', 'articlemeta.scielo.org:11620')

    return client.ThriftClient(domain=address)


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
    except ValueError:
        pages = 0

    if pages >= 0:
        return pages
    else:
        return 0


def acceptancedelta(received, accepted):

    try:
        rec = datetime.strptime(received, '%Y-%m-%d')
    except ValueError:
        return None

    try:
        acc = datetime.strptime(accepted, '%Y-%m-%d')
    except ValueError:
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


def documents(endpoint, collection=None, issns=None, fmt=None, from_date=FROM, until_date=UNTIL, identifiers=False):

    allowed_endpoints = ['journal', 'article']

    if not endpoint in allowed_endpoints:
        raise TypeError('Invalid endpoint, expected one of: %s' % str(allowed_endpoints))

    for issn in issns:
        if endpoint == 'article':
            if identifiers:
                itens = articlemeta().documents(collection=collection, issn=issn, from_date=from_date, until_date=until_date)
            else:
                itens = articlemeta().documents_history(collection=collection, from_date=from_date, until_date=until_date)
        elif endpoint == 'journal':
            if identifiers:
                itens = articlemeta().journals(collection=collection)
            else:
                itens = articlemeta().journals_history(collection=collection, from_date=from_date, until_date=until_date)

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

            if not doc_ret:
                continue

            yield ('add', fmt(doc_ret))


def setup_index(index):

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
        },
        "settings": {
            "index": {
                "number_of_shards": 5,
                "number_of_replicas": 2
            }
        }
    }

    try:
        ES.indices.create(index=index, body=journal_settings_mappings)
    except RequestError:
        logger.debug('Index already available')


def run(doc_type, index='publication', collection=None, issns=None, from_date=FROM, until_date=UNTIL, identifiers=False, sanitization=True):

    setup_index(index)

    if doc_type == 'journal':
        endpoint = 'journal'
        fmt = fmt_journal
    elif doc_type == 'article':
        endpoint = 'article'
        fmt = fmt_document
    else:
        logger.error('Invalid doc_type')
        exit()

    for event, document in documents(endpoint, collection=collection, issns=issns, fmt=fmt, from_date=from_date, until_date=until_date, identifiers=identifiers):
        if event == 'delete':
            logger.debug('removing document %s from index %s', document['id'], doc_type)
            try:
                ES.delete(index=index, doc_type=doc_type, id=document['id'])
            except NotFoundError:
                logger.debug('Record already removed: %s', document['id'])
            except:
                logger.error('Unexpected error: %s', sys.exc_info()[0])

        else:  # event would be ['add', 'update']
            logger.debug('loading document %s into index %s', document['id'], doc_type)
            ES.index(
                index=index,
                doc_type=doc_type,
                id=document['id'],
                body=document
            )

    if sanitization is True:
        logger.info("Running sanitization process")
        ind_ids = set()
        art_ids = set()

        logger.info("Loading ArticleMeta IDs")
        if doc_type == 'document':
            for issn in issns:
                for item in articlemeta().documents(collection=collection, issn=issn, only_identifiers=True):
                    code = '_'.join([item.collection, item.code])
                    art_ids.add(code)
                    logger.debug('Read item (%d): %s', len(art_ids), code)

        if doc_type == 'journal':
            for item in articlemeta().journals(collection=collection):
                code = '_'.join([item.collection_acronym, item.scielo_issn])
                art_ids.add(code)
                logger.debug('Read item (%d): %s', len(art_ids), code)

        logger.info("Loading Index IDs")
        body = {
            "query": {
                "match_all": {}
            },
            "_source": ["id"]
        }
        result = ES.search(index=index, doc_type=doc_type, body=body, size=10000, scroll='1h')
        while True:
            scroll = {
                'scroll': '1h',
                'scroll_id': result['_scroll_id']
            }
            if len(result['hits']['hits']) == 0:
                ES.clear_scroll(scroll_id=result['_scroll_id'])
                break
            for item in result['hits']['hits']:
                ind_ids.add(item['_id'])
                logger.debug('Read item (%d): %s', len(ind_ids), item['_id'])
            result = ES.scroll(body=scroll, scroll='1h')

        remove_ids = ind_ids - art_ids

        if endpoint == 'article' and len(remove_ids) > 2000:
            logger.warning('To many documents to remove (%d), skipping', len(remove_ids))
            return

        if endpoint == 'journal' and len(remove_ids) > 50:
            logger.warning('To many journals to remove (%d), skipping', len(remove_ids))
            return

        for item in remove_ids:
            logger.debug('Removing id: %s', item)
            ES.delete(index=index, doc_type=doc_type, id=item)


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
        '--until_date',
        '-u',
        default=UNTIL,
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
        '--sanitization',
        '-s',
        action='store_true',
        help='Run cleaup process. This process will remove from index, every ID not available in ArticleMeta'
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
        default=LOGGING_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()
    LOGGING['handlers']['console']['level'] = args.logging_level
    for lg, content in LOGGING['loggers'].items():
        content['level'] = args.logging_level

    logging.config.dictConfig(LOGGING)

    issns = None
    if len(args.issns) > 0:
        issns = utils.ckeck_given_issns(args.issns)

    run(args.doc_type, index=args.index, collection=args.collection, issns=issns or [None], from_date=args.from_date, until_date=args.until_date, identifiers=args.identifiers, sanitization=args.sanitization)
