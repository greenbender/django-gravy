from django.utils.six.moves.urllib.parse import unquote
from django.utils import timezone, six
from django.utils.encoding import force_text
from django.utils.safestring import SafeText, mark_safe
from django.utils.functional import allow_lazy
from django.template import Template, Context
from django.conf import settings
from collections import OrderedDict
from datetime import datetime as _datetime
import magic
import unicodedata
import mimetypes
import calendar
import weakref
import time
import os
import re


import logging
log = logging.getLogger('gravy.utils')


# TODO: check the datetime functions (do they do what is expected?)
def epoch(dt):
    """
    Convert a timezone aware datetime object to unix epoch timestamp.
    """
    if timezone.is_aware(dt):
        return int(calendar.timegm(dt.utctimetuple()))
    else:
        return int(time.mktime(dt.timetuple()))


def datetime(e):
    """
    Convert epoch to a datetime. If USE_TZ is set convert to to the current
    timezone, otherwise convert to naive localtime.
    """
    if settings.USE_TZ:
        return _datetime.fromtimestamp(e, timezone.get_current_timezone())
    return _datetime.fromtimestamp(e)


def seconds_to_units(seconds):
    """
    Converts number of seconds as a int into
    weeks, days, hours, minutes, seconds delta
    """
    minutes, seconds = divmod(seconds, 60)
    if not minutes:
        return (seconds, 'second')
    hours, minutes = divmod(minutes, 60)
    if not hours:
        return (minutes, 'minute')
    days, hours = divmod(hours, 24)
    if not days:
        return (hours, 'hour')
    weeks, days = divmod(days, 7)
    if not weeks:
        return (days, 'day')
    return (weeks, 'week')


def safepath(path):
    """
    Take an untrusted path (possibly urlencoded) return a path that is safe
    from directory traversal. Taken from django.views.static.
    """
    path = os.path.normpath(unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    return newpath


# we only want to do this once
_templify_template = Template('{{ obj }}')


def templify(obj):
    """
    Converts the object to a string as it would occur in a template if it
    were rendered inline ie. {{ variable }}. This is especially useful
    for datetime objects.
    """
    return _templify_template.render(Context({'obj': obj}))


def safe_meta(txt, tiny=True):
    """
    Remove excess whitespace and newlines. This allows us to use double
    newlines as a delimiter between metadata fields.
    """
    if tiny:
        return re.sub(r'\s+', ' ', txt)
    return re.sub(r'\n+', '\n',
        re.sub(r'(?m)^\s*$', '',
            re.sub(r'[ \t\r]+', ' ', txt)
        )
    )


def dict_meta(d):
    """
    Convert a dictionary to metadata.
    """
    return '\n'.join(
        [': '.join(map(str, [k, v])) for k, v in six.iteritems(d)]
    )


_hexdump_map = ''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])


def hexdump(src, length=16):
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(_hexdump_map)
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
    return ''.join(result)


def magic_mimetype(data='', filename=None):
    """
    Use libmagic to determine the mimetype of the given data (file content).
    """
    if filename is None:
        return magic.from_buffer(data, mime=True)
    return magic.from_file(filename, mime=True)


def magic_type(data='', filename=None):
    """
    Use libmagic to determine the mimetype of the given data (file content).
    """
    if filename is None:
        return magic.from_buffer(data)
    return magic.from_file(filename)


# use ours by preference
mimetypes.knownfiles = getattr(settings, 'MIMETYPES', mimetypes.knownfiles)
mimetypes.types_map = {}
mimetypes.init()


def magic_extension(mimetype):
    """
    Use the mimetype to determine the file extension of the given data (file
    content).
    """
    return mimetypes.guess_extension(mimetype)


class _DoesNotExist(object):
    def __str__(self):
        return ''
    def __unicode_(self):
        return u''
    def __bool__(self):
        return False
    def __nonzero__(self):
        return False
    def __int__(self):
        return 0


def islugify(value, allow_unicode=False):
    """
    Like slugify but doesn't change case.
    """
    # basically a clone of django.utils.text.slugify()
    value = force_text(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
        value = re.sub('[^\w\s-]', '', value, flags=re.U).strip()
        return mark_safe(re.sub('[-\s]+', '-', value, flags=re.U))
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip()
    return mark_safe(re.sub('[-\s]+', '-', value))
islugify = allow_lazy(islugify, six.text_type, SafeText)


DoesNotExist = _DoesNotExist()
