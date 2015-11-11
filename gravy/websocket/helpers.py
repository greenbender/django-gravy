import json


import logging
log = logging.getLogger('gravy.websocket.helpers')


__all__ = ['serialize', 'deserialize',]


class _AlwaysEncode(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            pass
        return unicode(obj)


def serialize(obj):
    return json.dumps(obj, cls=_AlwaysEncode)


def deserialize(data):
    return json.loads(data)
