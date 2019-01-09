from geventwebsocket import WebSocketError
from django_redis import get_redis_connection
from .helpers import serialize, deserialize
import gevent
import fnmatch
import os


import logging
log = logging.getLogger('gravy.websocket.redis')


__all__ = ['RedisPubsubRegistry', 'RedisMixin', 'RedisRoomsMixin',]


_redis_conn = get_redis_connection('default')


class _RedisPubsubRegistry(object):

    def __init__(self, conn):
        self._registry = {}
        self.conn = conn
        self.sub_channel = 'redispubsubregistry:sub:%d:%d' % (os.getpid(), hash(self))
        self.unsub_channel = 'redispubsubregistry:unsub:%d:%d' % (os.getpid(), hash(self))
        self.task = gevent.spawn(self.listener)

    def listener(self):
        pubsub = self.conn.pubsub()
        pubsub.subscribe(self.sub_channel)
        pubsub.subscribe(self.unsub_channel)
        try:
            for msg in pubsub.listen():
                # ignore non-messages
                if msg['type'] not in ('message', 'pmessage'):
                    continue
                # subscribe to channel
                if msg['channel'] == self.sub_channel:
                    pubsub.psubscribe(msg['data'])
                    continue
                # unsubscribe from channel
                if msg['channel'] == self.unsub_channel:
                    pubsub.punsubscribe(msg['data'])
                    continue
                # emit messages to namespace handlers
                for channel, handlers in self._registry.items():
                    if not fnmatch.fnmatch(msg['channel'], channel):
                        continue
                    for handler in handlers:
                        handler.check_and_send(msg)
        except ConnectionError:
            pass

    def publish(self, channel, msg):
        """
        Convienience method for publishing.
        """
        return self.conn.publish(channel, msg)

    def register(self, channel, handler):
        if channel not in self._registry:
            self._registry[channel] = []
            self.conn.publish(self.sub_channel, channel)
        if handler not in self._registry[channel]:
            self._registry[channel].append(handler)

    def unregister(self, channel, handler):
        if channel in self._registry:
            if handler in self._registry[channel]:
                self._registry[channel].remove(handler)
                if not self._registry[channel]:
                    self.conn.publish(self.unsub_channel, channel)
                    del self._registry[channel]


RedisPubsubRegistry = _RedisPubsubRegistry(_redis_conn)
"""Redis Pubsub registry singleton."""


class RedisMixin(object):
    event = 'update'

    def __init__(self, *args, **kwargs):
        super(RedisMixin, self).__init__(*args, **kwargs)
        RedisPubsubRegistry.register(self.get_channel(), self)

    def cleanup(self):
        RedisPubsubRegistry.unregister(self.get_channel(), self)
        super(RedisMixin, self).cleanup()

    @classmethod
    def get_channel(cls):
        return cls.channel

    @classmethod
    def publish(cls, channel=None, **data):
        channel = channel or cls.get_channel()
        RedisPubsubRegistry.publish(channel, serialize(data))

    def check_and_send(self, msg):
        try:
            self.send(self.event, **deserialize(msg['data']))
        except WebSocketError as e:
            log.debug(e)
            self.stop()
        except Exception as e:
            log.error(e)
            self.stop()


class RedisRoomsMixin(object):

    def __init__(self, *args, **kwargs):
        self.rooms = set()
        super(RedisRoomsMixin, self).__init__(*args, **kwargs)

    @classmethod
    def _get_room_name(cls, room):
        return '.'.join([cls.channel, str(room)])

    @classmethod
    def get_channel(cls):
        return super(RedisRoomsMixin, cls).get_channel() + '.*'

    @classmethod
    def publish(cls, room, channel=None, **data):
        if channel is None:
            channel = cls._get_room_name(room)
        super(RedisRoomsMixin, cls).publish(channel=channel, **data)

    def join(self, room):
        self.rooms.add(self._get_room_name(room))

    def leave(self, room):
        self.rooms.remove(self._get_room_name(room))

    def on_join(self, room):
        self.join(room)

    def on_leave(self, room):
        self.leave(room)

    def check_and_send(self, msg):
        if msg['channel'] in self.rooms:
            super(RedisRoomsMixin, self).check_and_send(msg)
