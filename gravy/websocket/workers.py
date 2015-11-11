from geventwebsocket.gunicorn.workers import GeventWebSocketWorker
from .handler import DjangoWebSocketHandler


class DjangoWebSocketWorker(GeventWebSocketWorker):
    wsgi_handler = DjangoWebSocketHandler
