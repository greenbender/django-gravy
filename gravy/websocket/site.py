from django.conf.urls import url
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .namespace import NamespaceHandlerRegistry


import logging
log = logging.getLogger('gravy.websocket')


__all__ = ['urls',]


@csrf_exempt
def ws(request, namespace=None):
    handler_class = NamespaceHandlerRegistry.get(namespace)
    handler_class(request).run()
    return HttpResponse()


urls = [url(r'^(?P<namespace>\w+)$', ws)]
