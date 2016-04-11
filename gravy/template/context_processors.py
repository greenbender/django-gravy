from django.conf import settings


DEFAULT_TIMEZONES = ['UTC']


def tz(request):
    from django.utils import timezone
    context = {'TIME_ZONE': timezone.get_current_timezone_name()}
    if hasattr(settings, 'TIMEZONES'):
        context['TIMEZONES'] = settings.TIMEZONES
    else:
        try:
            import pytz
            context['TIMEZONES'] = pytz.common_timezones
        except ImportError:
            context['TIMEZONES'] = DEFAULT_TIMEZONES
    return context
