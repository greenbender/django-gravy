from django import template
from django.template.defaultfilters import pluralize
from ..utils import seconds_to_units


register = template.Library()


@register.filter
def humanize_seconds(value):
    qty, unit = seconds_to_units(abs(value))
    unit += pluralize(qty) 
    if value < 0:
        qty = -qty 
    return "{0} {1}".format(qty, unit)


@register.filter(name='getattr', is_safe=False)
def _getattr(value, arg):
    try:
        return value[arg]
    except (KeyError, TypeError, IndexError):
        pass
    return getattr(value, arg)
