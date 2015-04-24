from pyramid.view import view_config
from pyramid.response import Response
import pyramid.httpexceptions as exc

@view_config(route_name='index', request_method='GET')
def index(request):
    return Response('Publication Stats by SciELO API')

@view_config(route_name='journals', request_method='GET', renderer='jsonp')
def journals_collection(request):
    collection = request.GET.get('collection', None)
    issn = request.GET.get('issn', None)
    subject_area = request.GET.get('subject_area', None)
    journal = request.GET.get('journal', None)
    aggs = request.GET.get('aggs', None)

    if not aggs:
        raise exc.HTTPBadRequest("aggs parameter is required")

    filters = {}
    if collection:
        filters['collection'] = collection
    if issn:
        filters['issn'] = issn
    if subject_area:
        filters['subject_areas'] = subject_area
    if journal:
        filters['journal'] = journal

    try:
        data = request.index.publication_stats(doc_type='journal', filters=filters, aggs=aggs.split(','))
    except ValueError as error:
        raise exc.HTTPBadRequest(error.message)

    return data

@view_config(route_name='documents', request_method='GET', renderer='jsonp')
def documents_collection(request):

    collection = request.GET.get('collection', None)
    issn = request.GET.get('issn', None)
    subject_area = request.GET.get('subject_area', None)
    affiliation_country = request.GET.get('affiliation_country', None)
    publication_year = request.GET.get('publication_year', None)
    document_type = request.GET.get('document_type', None)
    language = request.GET.get('language', None)
    aggs = request.GET.get('aggs', None)

    if not aggs:
        raise exc.HTTPBadRequest("aggs parameter is required")

    filters = {}
    if collection:
        filters['collection'] = collection
    if issn:
        filters['issn'] = issn
    if subject_area:
        filters['subject_areas'] = subject_area
    if affiliation_country:
        filters['aff_countries'] = affiliation_country
    if publication_year:
        filters['publication_year'] = publication_year
    if document_type:
        filters['document_type'] = document_type
    if language:
        filters['languages'] = language

    try:
        data = request.index.publication_stats(doc_type='article', filters=filters, aggs=aggs.split(','))
    except ValueError as error:
        raise exc.HTTPBadRequest(error.message)

    return data