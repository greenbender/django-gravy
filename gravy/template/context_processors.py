def tz(request):
    from django.utils import timezone
    context = {'TIME_ZONE': timezone.get_current_timezone_name()}
    try:
        import pytz
        context['TIMEZONES'] = pytz.common_timezones
    except ImportError:
        pass
    return context
