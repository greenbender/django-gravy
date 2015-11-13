from django.db import models
from django.conf import settings

from .registration import CurrentUserFieldRegistry


class CurrentUserField(models.ForeignKey):

    def __init__(self, auto_user=False, auto_user_add=False, **kwargs):
        kwargs['to'] = settings.AUTH_USER_MODEL
        kwargs.setdefault('null', True)
        kwargs.setdefault('editable', False)
        self.auto_user = auto_user
        self.auto_user_add = auto_user_add
        super(CurrentUserField, self).__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(CurrentUserField, self).deconstruct()
        # XXX: should be able to del 'to' keyword but there is a bug
        # Check https://code.djangoproject.com/ticket/24434#ticket for a
        #       resolution every now and then
        #del kwargs['to']
        if kwargs['null'] is True:
            del kwargs['null']
        if kwargs['editable'] is False:
            del kwargs['editable']
        if self.auto_user:
            kwargs['auto_user'] = True
        if self.auto_user_add:
            kwargs['auto_user_add'] = True
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name):
        super(CurrentUserField, self).contribute_to_class(cls, name)
        if not cls._meta.abstract:
            registry = CurrentUserFieldRegistry()
            registry.add_field(cls, self)

