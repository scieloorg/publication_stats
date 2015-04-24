from pyramid.renderers import JSONP
from pyramid.config import Configurator
from pyramid.settings import aslist, asbool

from publication import controller

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_renderer('jsonp', JSONP(param_name='callback', indent=4))

    hosts = aslist(settings['elasticsearch'])

    def add_index(request):
        return controller.stats(hosts=hosts, sniff_on_start=True, 
            sniff_on_connection_fail=True)

    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('journals', '/api/v1/journals')
    config.add_route('documents', '/api/v1/documents')
    config.add_request_method(add_index, 'index', reify=True)
    config.scan()
    return config.make_wsgi_app()
