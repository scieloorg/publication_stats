# coding: utf-8
import json
import argparse
import logging
import os
import sys

from publication.controller import stats, ServerError

import thriftpy
from thriftpy.thrift import TProcessor


logger = logging.getLogger(__name__)

publication_stats_thrift = thriftpy.load(
    os.path.dirname(__file__)+'/publication_stats.thrift',
    module_name='publication_stats_thrift'
)

class Dispatcher(object):

    def __init__(self):

        self._stats = stats()

    def _stats_dispatcher(self, *args, **kwargs):

        try:
            data = self._stats.publication_stats(*args, **kwargs)
        except ValueError as e:
            logging.error(e.message)
            raise publication_stats_thrift.ValueError(message=e.message)
        except ServerError as e:
            raise publication_stats_thrift.ServerError(message=e.message)

        return data

    def query(self, doc_type, body, parameters):

        params = {i.key:i.value for i in parameters}
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

    def journal_subject_areas(self, filters=None):

        data = self._stats_dispatcher('journal', 'subject_areas', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def journal_collections(self, filters=None):

        data = self._stats_dispatcher('journal', 'collection', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def journal_statuses(self, filters=None):

        data = self._stats_dispatcher('journal', 'status', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def journal_inclusion_years(self, filters=None):

        data = self._stats_dispatcher('journal', 'included_at_year', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_subject_areas(self, filters=None):

        data = self._stats_dispatcher('article', 'subject_areas', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_collections(self, filters=None):

        data = self._stats_dispatcher('article', 'collection', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_publication_years(self, filters=None):

        data = self._stats_dispatcher('article', 'publication_year', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_languages(self, filters=None):

        data = self._stats_dispatcher('article', 'languages', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_affiliation_countries(self, filters=None):

        data = self._stats_dispatcher('article', 'aff_countries', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_types(self, filters=None):

        data = self._stats_dispatcher('article', 'document_type', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]


app = TProcessor(publication_stats_thrift.PublicationStats, Dispatcher())
