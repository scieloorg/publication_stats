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
import xylose

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
        'ARTICLEMETA_THRIFTSERVER', 'articlemeta.scielo.org:11621')

    return client.ThriftClient(domain=address)


def fmt_journal(document):
    data = {}

    data['id'] = '_'.join([document.collection_acronym, document.scielo_issn])
    data['issn'] = document.scielo_issn
    data['collection'] = document.collection_acronym
    data['creation_year'] = document.creation_date[0:4]
    data['creation_date'] = document.creation_date
    data['processing_year'] = document.processing_date[0:4]
    data['processing_date'] = document.processing_date
    data['subject_areas'] = document.subject_areas or ['undefined']
    data['subject_areas'] = ['Multidisciplinary'] if len(data['subject_areas']) > 2 else data['subject_areas']
    data['is_multidisciplinary'] = 1 if len(data['subject_areas']) > 2 else 0
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
    except TypeError:
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
    except TypeError:
        return None

    try:
        acc = datetime.strptime(accepted, '%Y-%m-%d')
    except ValueError:
        return None
    except TypeError:
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
    data['subject_areas'] = document.journal.subject_areas or ['undefined']
    data['subject_areas'] = ['Multidisciplinary'] if len(data['subject_areas']) > 2 else data['subject_areas']
    data['is_multidisciplinary'] = 1 if len(data['subject_areas']) > 2 else 0
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
        data['aff_states_code'] = list(set([state(
            aff.get('state', 'undefined'),
            country(aff.get('country', 'undefined'))) for aff in document.mixed_affiliations]))
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


def documents(endpoint, collection=None, issns=None, fmt=None, from_date=FROM, until_date=UNTIL):

    allowed_endpoints = ['journal', 'article']

    if endpoint not in allowed_endpoints:
        raise TypeError('Invalid endpoint, expected one of: %s' % str(allowed_endpoints))

    for issn in issns:
        if endpoint == 'article':
            itens = articlemeta().documents(collection=collection, issn=issn, from_date=from_date, until_date=until_date)
        elif endpoint == 'journal':
            itens = articlemeta().journals(collection=collection)

        for item in itens:
            if not item or not item.data:
                continue

            formated_document = fmt(item)

            yield ('add', formated_document)


def setup_index(index):

    logger.info('Setting up index %s', index)

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
                    "is_multidisciplinary": {
                        "type": "long"
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
                    "is_multidisciplinary": {
                        "type": "long"
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


def differential_mode(index, endpoint, fmt, collection=None, delete=False):
    art_meta = articlemeta()
    logger.info("Running differetial process")
    ind_ids = set()
    art_ids = set()
    logger.info("Loading ArticleMeta IDs")
    if endpoint == 'article':
        for ndx, item in enumerate(art_meta.documents(collection=collection, only_identifiers=True), 1):
            code = '_'.join([item.collection, item.code, item.processing_date])
            art_ids.add(code)
            logger.debug('Read item from ArticleMeta (%d): %s', ndx, code)

    if endpoint == 'journal':
        for ndx, item in enumerate(art_meta.journals(collection=collection), 1):
            code = '_'.join([item.collection_acronym, item.scielo_issn, item.processing_date])
            art_ids.add(code)
            logger.debug('Read item from ArticleMeta (%d): %s', ndx, code)

    logger.info("Loading ElasticSearch Index IDs")

    if collection:
        query = {
            "match": {
                "collection": collection

            }
        }
    else:
        query = {
            "match_all": {}
        }

    body = {
        "query": query,
        "_source": ["id", "processing_date"]
    }

    result = ES.search(index=index, doc_type=endpoint, body=body, size=10000, scroll='1h')
    ndx = 0
    while True:
        scroll = {
            'scroll': '1h',
            'scroll_id': result['_scroll_id']
        }
        if len(result['hits']['hits']) == 0:
            ES.clear_scroll(scroll_id=result['_scroll_id'])
            break
        for item in result['hits']['hits']:
            ndx += 1
            code = "_".join([item['_source']['id'], item['_source'].get('processing_date', '1900-01-01')])
            ind_ids.add(code)
            logger.debug('Read item from ElasticSearch Index (%d): %s', ndx, code)
        result = ES.scroll(body=scroll, scroll='1h')

    # Ids to include
    logger.info("Running include records process.")
    include_ids = art_ids - ind_ids
    total_to_include = len(include_ids)
    logger.info("Including (%d) documents to search index." % total_to_include)
    if total_to_include > 0:
        for ndx, to_include_id in enumerate(include_ids, 1):
            logger.debug("Including documento (%d/%d): %s" % (ndx, total_to_include, to_include_id))
            splited = to_include_id.split('_')
            code = splited[1]
            collection = splited[0]
            processing_date = splited[2]
            if endpoint == 'article':
                document = art_meta.document(code=code, collection=collection)
                try:
                    document = fmt(document)
                except xylose.scielodocument.UnavailableMetadataException as e:
                    logger.error('Fail to format metadata for (%s_%s) error: %s', collection, code, e.args[0])
                    continue

            if endpoint == 'journal':
                document = art_meta.journal(code=code, collection=collection)
                try:
                    document = fmt(document)
                except xylose.scielodocument.UnavailableMetadataException as e:
                    logger.error('Fail to format metadata for (%s_%s) error: %s', collection, code, e.args[0])
                    continue

            ES.index(index=index, doc_type=endpoint, id=document['id'], body=document)

    # Ids to remove
    if delete is True:
        logger.info("Running remove records process.")
        remove_ids = set([i.split('_')[1] for i in ind_ids]) - set([i.split('_')[1] for i in art_ids])
        total_to_remove = len(remove_ids)
        logger.info("Removing (%d) documents to search index." % total_to_remove)
        if endpoint == 'article' and total_to_remove > 1000:
            logger.warning('To many documents to remove (%d), skipping', total_to_remove)
            return

        if endpoint == 'journal' and total_to_remove > 10:
            logger.warning('To many journals to remove (%d), skipping', total_to_remove)
            return

        for ndx, to_remove_id in enumerate(remove_ids, 1):
            logger.debug('Removing document (%d/%d): %s', ndx, total_to_remove, to_remove_id)
            splited = to_remove_id.split('_')
            code = '_'.join([splited[0], splited[1]])
            collection = splited[0]
            processing_date = splited[2]
            ES.delete(index=index, doc_type=endpoint, id=code)


def common_mode(
    index, endpoint, fmt, collection=None, issns=None, from_date=FROM,
    until_date=UNTIL, delete=False
):

    logger.info('Running common mode')

    for event, document in documents(
        endpoint, collection=collection, issns=issns, fmt=fmt,
        from_date=from_date, until_date=until_date
    ):

        logger.debug('loading document %s into index %s', document['id'], endpoint)
        ES.index(
            index=index,
            doc_type=endpoint,
            id=document['id'],
            body=document
        )


def run(
    doc_type, index=utils.ELASTICSEARCH_INDEX, collection=None, issns=None,
    from_date=FROM, until_date=UNTIL, differential=False, delete=False
):

    logger.info('Running Publication Stats Update')

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

    logger.info('Updating %s index', index)

    if differential is True:
        differential_mode(
            index, endpoint, fmt, collection=collection, delete=delete)
    else:
        common_mode(index, endpoint, fmt, collection, issns, from_date, until_date)

    logger.info('Processing finished')


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
        '-i',
        default=utils.ELASTICSEARCH_INDEX,
        help='Define the source index to populate.'
    )

    parser.add_argument(
        '--differential',
        '-x',
        action='store_true',
        help='Differential processing compare ids from ArticleMeta and PublicationStats index, remove and add just the diferences between both sources.'
    )

    parser.add_argument(
        '-d', '--delete',
        default=False,
        action='store_true',
        help='Remove documents elegible to be removed in differential process'
    )

    parser.add_argument(
        '--doc_type',
        '-t',
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
    for content in LOGGING['loggers'].values():
        content['level'] = args.logging_level

    logging.config.dictConfig(LOGGING)

    issns = None
    if len(args.issns) > 0:
        issns = utils.ckeck_given_issns(args.issns)

    run(
        args.doc_type,
        index=args.index, collection=args.collection,
        issns=issns or [None], from_date=args.from_date,
        until_date=args.until_date, differential=args.differential,
        delete=args.delete
    )
