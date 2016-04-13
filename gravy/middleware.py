import pytz
from django.db.models import signals
from django.utils import timezone
from django.contrib.auth.middleware import RemoteUserMiddleware
from .db.models.registration import CurrentUserFieldRegistry


import logging
log = logging.getLogger('gravy.middleware')


__all__ = [
    'DebugMiddleware', 'NginxRemoteUserMiddleware', 'CurrentUserMiddleware',
    'TimezoneMiddleware',
]


class DebugMiddleware(object):

    def process_request(self, request):
        log.error(request.META)


class NginxRemoteUserMiddleware(RemoteUserMiddleware):
    header = 'HTTP_REMOTE_USER'


class CurrentUserMiddleware(object):

    def process_request(self, request):
        if request.method in ('GET', 'HEAD', 'OPTION', 'TRACE'):
            return
        if hasattr(request, 'user') and request.user.is_authenticated():
            user = request.user
        else:
            user = None
        def update_user_fields(sender, instance, **kwargs):
            registry = CurrentUserFieldRegistry()
            if sender in registry:
                for field in registry.get_fields(sender):
                    # XXX: this isn't a great check for add but i'm not sure
                    # of a better way at this point
                    add = instance.pk is None and getattr(instance, field.name) is None
                    if field.auto_user or (field.auto_user_add and add):
                        setattr(instance, field.name, user)
        signals.pre_save.connect(update_user_fields, dispatch_uid=request, weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=request)
        return response


# from https://docs.djangoproject.com/en/1.9/topics/i18n/timezones/
class TimezoneMiddleware(object):

    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
