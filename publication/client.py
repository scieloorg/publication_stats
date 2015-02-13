# coding: utf-8
import thriftpy

publication_stats_thrift = thriftpy.load(
    'publication_stats.thrift',
    module_name='publication_stats_thrift'
)

from thriftpy.rpc import make_client

client = make_client(
    publication_stats_thrift.PublicationStats,
    'nefertiti.scielo.org',
    11600
)