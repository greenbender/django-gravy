from django.utils.module_loading import autodiscover_modules


import logging
log = logging.getLogger('gravy.websocket')


__all__ = ['autodiscover',]


def autodiscover():
    autodiscover_modules('sockets')
