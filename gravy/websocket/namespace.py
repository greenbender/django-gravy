from geventwebsocket import WebSocketError
from .redis import RedisMixin, RedisRoomsMixin
from .helpers import serialize, deserialize
import gevent


import logging
log = logging.getLogger('gravy.websocket.namespace')


__all__ = [
    'NamespaceHandlerRegistry', 'BaseNamespace', 'JsonNamespace',
    'RedisNamespace', 'RedisRoomsNameSpace'
]


class _NamespaceHandlerRegistry(object):
    """
    Registry for keeping track of namespace handlers.
    """

    def __init__(self):
        self._registry = {}

    def register(self, channel, handler):
        self._registry[channel] = handler

    def __getitem__(self, channel):
        return self._registry[channel]

    def get(self, channel):
        return self[channel]


NamespaceHandlerRegistry = _NamespaceHandlerRegistry()
"""Namespace registry singleton."""


class namespace(object):
    """
    Decorator for Namespace handlers.
    """
    registry = NamespaceHandlerRegistry

    def __init__(self, channel=''):
        self.channel = channel
 
    def __call__(self, handler):
        handler.channel = self.channel
        self.registry.register(self.channel, handler)
        return handler


class BaseNamespace(object):
    """
    Base Namespace handler.
    """
    socket_name = 'wsgi.websocket'
    channel = None

    def __init__(self, request):
        self.request = request
        self.environ = self.get_environ()
        self.socket = self.get_socket()
        self.running = False

    def get_environ(self):
        return self.request.environ

    def get_socket(self):
        return self.environ[self.socket_name]
    
    def recv(self):
        return self.socket.receive()
    
    def send(self, pkt):
        self.socket.send(pkt)
 
    def setup(self):
        pass

    def cleanup(self):
        pass

    def run(self):
        self.running = True
        self.setup()
        try:
            while self.running:
                self.recv()
        except WebSocketError as e:
            log.debug(e)
        except Exception as e:
            log.error(e)
        finally:
            self.stop()
            self.cleanup()

    def stop(self):
        self.running = False

class JsonNamespace(BaseNamespace):
    """
    JsonNamespace handler.
    """
    ping_timeout = 30
    
    def recv(self):
        pkt = super(JsonNamespace, self).recv()
        if pkt is None:
            return
        msg = deserialize(pkt)
        if 'event' not in msg:
            log.error('Invalid Websocket packet')
            return
        method = getattr(self, 'on_' + msg['event'], None)
        if method is None:
            return
        data = msg.get('data', None)
        return method(data)
    
    def send(self, event, **data):
        msg = {'event': event}
        if data:
            msg['data'] = data
        pkt = serialize(msg)
        super(JsonNamespace, self).send(pkt)
 
    def ping_run(self):
        try:
            while not self.ping_event.wait(self.ping_timeout):
                self.send('ping')
        except WebSocketError as e:
            log.debug(e)
        except Exception as e:
            log.error(e)
        finally:
            self.stop()

    def setup(self):
        super(JsonNamespace, self).setup()
        if self.ping_timeout is not None:
            self.ping_event = gevent.event.Event()
            self.ping_task = gevent.spawn(self.ping_run)
        
    def cleanup(self):
        if self.ping_timeout is not None:
            self.ping_event.set()
            self.ping_task.join()
        super(JsonNamespace, self).cleanup()


class RedisNamespace(RedisMixin, JsonNamespace):
    pass


class RedisRoomsNamespace(RedisRoomsMixin, RedisMixin, JsonNamespace):
    pass
