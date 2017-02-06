# coding: utf-8
import json
import argparse
import logging
import os
import sys

from publication.controller import stats, ServerError

import thriftpy
import thriftpywrap
from thriftpy.rpc import make_server

from publication import utils

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
        'publication.thrift.server': {
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

publication_stats_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__), 'publication_stats.thrift'))


class Dispatcher(object):

    def __init__(self):

        config = utils.Configuration.from_env()
        settings = dict(config.items())

        es_params = {
            'hosts': settings['app:main']['elasticsearch'],
            'timeout': 60
        }

        self._stats = stats(**es_params)

    def _stats_dispatcher(self, *args, **kwargs):

        try:
            data = self._stats.publication_stats(*args, **kwargs)
        except ValueError as e:
            logging.error(e.message)
            raise publication_stats_thrift.ValueError(message=e.message)
        except ServerError as e:
            raise publication_stats_thrift.ServerError(message=e.message)

        return data

    def search(self, doc_type, body, parameters):

        params = {i.key: i.value for i in parameters}
        params['doc_type'] = doc_type
        params['body'] = json.loads(body)

        try:
            data = self._stats.publication_search(params)
        except ValueError as e:
            logging.error(e.message)
            raise publication_stats_thrift.ValueError(message=e.message)
        except ServerError as e:
            raise publication_stats_thrift.ServerError(message=e.message)

        try:
            data_str = json.dumps(data)
        except ValueError as e:
            logging.error('Invalid JSON data: %s' % data_str)
            raise publication_stats_thrift.ValueError(message=e.message)

        return data_str

    def journal(self, aggs=None, filters=None):

        try:
            data = self._stats_dispatcher('journal', aggs=aggs, filters=filters)
        except ValueError as err:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server: %s' % err.message
            )

        result = json.dumps(data)

        return result


    def journal_subject_areas(self, filters=None):

        data = self._stats_dispatcher('journal', aggs=['subject_areas'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['subject_areas']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def journal_collections(self, filters=None):

        data = self._stats_dispatcher('journal', aggs=['collection'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['collection']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def journal_statuses(self, filters=None):

        data = self._stats_dispatcher('journal', aggs=['status'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['status']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def journal_inclusion_years(self, filters=None):

        data = self._stats_dispatcher('journal', aggs=['included_at_year'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['included_at_year']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def document_subject_areas(self, filters=None):

        data = self._stats_dispatcher('article', aggs=['subject_areas'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['subject_areas']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def document(self, aggs=None, filters=None):

        try:
            data = self._stats_dispatcher('article', aggs=aggs, filters=filters)
        except ValueError as err:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server: %s' % err.message
            )

        result = json.dumps(data)

        return result

    def document_collections(self, filters=None):

        data = self._stats_dispatcher('article', aggs=['collection'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['collection']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def document_publication_years(self, filters=None):

        data = self._stats_dispatcher('article', aggs=['publication_year'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['publication_year']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def document_languages(self, filters=None):

        data = self._stats_dispatcher('article', aggs=['languages'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['languages']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def document_affiliation_countries(self, filters=None):

        data = self._stats_dispatcher('article', aggs=['aff_countries'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['aff_countries']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result

    def document_types(self, filters=None):

        data = self._stats_dispatcher('article', aggs=['document_type'], filters=filters)

        try:
            result = [publication_stats_thrift.aggs(key=item['key'], count=item['doc_count']) for item in data['document_type']['buckets']]
        except:
            raise publication_stats_thrift.ServerError(
                'Fail to retrieve data from server'
            )

        return result


main = thriftpywrap.ConsoleApp(publication_stats_thrift.PublicationStats, Dispatcher)
