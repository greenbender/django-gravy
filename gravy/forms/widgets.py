from django.forms.widgets import *
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django.forms.utils import flatatt
from django.utils import six
from django.core.files import File
from django.http import QueryDict
from ..utils import datetime
from collections import OrderedDict
import urlparse
import re


import logging
log = logging.getLogger('gravy.forms.widgets')


__all__ = [
    'NamedMultiWidget', 'RepeatNamedMultiWidget', 'ParsedURLInput',
    'SeparatedWidgetMixin', 'SeparatedMultipleWidgetMixin', 'SeparatedSelect',
    'SeparatedSelectMultiple', 'SeparatedTextInput', 'SeparatedTextarea',
    'SerializedDateTimeInput', 'MultipleFileInput', 'DateTimeRangeInput',
    'DependsWidget',
]
# proxy django.forms.widgets
import django.forms.widgets
__all__.extend(django.forms.widgets.__all__)


# XXX: don't bother inheriting here? Use lower level mixins?
# XXX: implement __deepcopy__
class NamedMultiWidget(MultiWidget):
    widgets = ()
    subwidget_name_format = '{0}.{1}'
    classname = 'named-multi-widget'
    template_name = 'gravy/forms/widgets/namedmultiwidget.html'

    class Media:
        css = {
            'all': ('css/jquery.namedMultiWidget.css',)
        }

    def __init__(self, widgets=None, attrs=None, labels=None, help_texts=None, initial=None):
        self.named_widgets = OrderedDict(widgets or self.widgets)
        self._labels = labels or {}
        self._help_texts = help_texts or {}
        self._initial = initial or {}
        widgets = self.named_widgets.values()
        super(NamedMultiWidget, self).__init__(widgets, attrs=attrs)

    def get_context(self, name, value, attrs=None):
        context = super(NamedMultiWidget, self).get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        if not isinstance(value, list):
            value = self.decompress(value)
        subwidgets = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        for i, subwidget in enumerate(self.named_widgets.items()):
            widget_name, widget = subwidget
            widget_attrs = dict(final_attrs)
            widget_attrs.pop('id', None)
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            subwidget_name = self.subwidget_name_format.format(name, widget_name)
            output = widget.get_context(subwidget_name, widget_value, widget_attrs)['widget']
            label = self._labels.get(widget_name,'')
            output['label_tag'] = {'label': self._labels.get(widget_name,''), 'attrs':flatatt({'title':self._help_texts.get(widget_name)})}
            subwidgets.append(output)
        context['widget']['subwidgets'] = subwidgets
        return context

    def id_for_label(self, id_):
        return id_

    def value_from_datadict(self, data, files, name):
        value = []
        for widget_name, widget in six.iteritems(self.named_widgets):
            widget_name = self.subwidget_name_format.format(name, widget_name)
            value.append(widget.value_from_datadict(data, files, widget_name))
        return value

    def decompress(self, value):
        if value:
            return [value.get(name, None) for name in self.named_widgets.keys()]
        return [None]*len(self.named_widgets)


# TODO: cleanup rendering attrs etc
class RepeatNamedMultiWidget(NamedMultiWidget):

    widget_class = 'repeat-named-multi-widget'
    toggle = 'repeatNamedMultiWidget'
    template_name = 'gravy/forms/widgets/repeatnamedmultiwidget.html'
    repeat_template_name = 'gravy/forms/widgets/datarepeattemplate.html'
    _nin_re = re.compile(r'(?P<name>[^\[]+)\[(?P<index>\d+)\](?P<next>.*)')

    class Media:
        css = {
            'all': ('css/jquery.repeatNamedMultiWidget.css',)
        }
        js = ('js/jquery.repeatNamedMultiWidget.js',)
    
    def _get_lists(self, d):
        if hasattr(d, 'lists'):
            return d.lists()
        return [(n, [v]) for n, v in d.items()]

    def _get_subquerydicts(self, name, querydict):
        subquerydicts = {}
        querylists = self._get_lists(querydict)
        for n, valuelist in querylists:
            match = self._nin_re.match(n)
            if match is None or match.group('name') != name:
                continue
            index = int(match.group('index'))
            subquerydicts.setdefault(index, QueryDict(mutable=True))
            subquerydicts[index].setlist(name + match.group('next'), valuelist)
        return subquerydicts

    def value_from_datadict(self, data, files, name):
        dsqd = self._get_subquerydicts(name, data)
        fsqd = self._get_subquerydicts(name, files)
        dfsqd = {}
        for i in dsqd:
            dfsqd[i] = (dsqd[i], fsqd.pop(i, {}))
        for i in fsqd:
            dfsqd[i] = ({}, fsqd[i])
        dfsql = [dfsqd[i] for i in sorted(dfsqd)]
        value = []
        for data, files in dfsql:
            value.append(super(RepeatNamedMultiWidget, self).value_from_datadict(data, files, name))
        return value

    def get_context(self, name, value, attrs=None):
        name += '[]'
        final_attrs = self.build_attrs(attrs)
        widget_attrs = dict(final_attrs)
        widget_attrs.pop('id', None)
        template_value = self._initial
        if not isinstance(value, list):
            template_value, value = value, []
        context = super(RepeatNamedMultiWidget, self).get_context(name, template_value, widget_attrs)
        context['widget']['attrs']['class']= self.widget_class
        context['widget']['attrs']['data-toggle']=self.toggle
        repeat_template = self._render(self.repeat_template_name, context)
        context['widget']['attrs']['data-repeat-template']= escape(repeat_template)
        rendered_widgets = []
        for i, val in enumerate(value):
            rendered_widgets.append(super(RepeatNamedMultiWidget, self).get_context(name, val, widget_attrs)['widget'])
        if rendered_widgets:
            context['widget']['rendered_widgets'] = rendered_widgets
        return context

class DependsWidget(CheckboxInput):
    classname = 'depends-widget'

    class Media:
        js = ('js/jquery.dependsWidget.js',)

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}
        attrs['class'] = self.classname
        super(DependsWidget, self).__init__(attrs=attrs, *args, **kwargs)


class ParsedURLInput(URLInput):
    attribute_map = (
        'scheme',
        'netloc',
        'path',
        'query',
        'fragment',
    )

    def get_context(self, name, value, attrs=None):
        if isinstance(value, dict):
            split = [value.get(n) for n in self.attribute_map]
            value = urlparse.urlunsplit(split)
        return super(ParsedURLInput, self).get_context(name, value, attrs=attrs)


class SeparatedBaseMixin(object):

    def __init__(self, attrs=None, token=',', cleanup=True, **kwargs):
        self.token = token
        self.cleanup = cleanup
        super(SeparatedBaseMixin, self).__init__(attrs=attrs, **kwargs)

    def _unsplit_value(self, value):
        if isinstance(value, list):
            value = self.token.join([unicode(v) for v in value])
        return value

    def _split_value(self, value):
        if isinstance(value, six.string_types):
            value = value.split(self.token)
            if self.cleanup:
                value = filter(bool, [v.strip() for v in value])
        return value


class SeparatedWidgetMixin(SeparatedBaseMixin):

    def get_context(self, name, value, attrs=None, **kwargs):
        value = self._unsplit_value(value)
        return super(SeparatedWidgetMixin, self).get_context(name, value, attrs=attrs, **kwargs)

    def value_from_datadict(self, data, files, name):
        value = super(SeparatedWidgetMixin, self).value_from_datadict(data, files, name)
        return self._split_value(value)


class SeparatedMultipleWidgetMixin(SeparatedBaseMixin):

    def get_context(self, name, value, attrs=None, **kwargs):
        if isinstance(value, (list, tuple)):
            value = [self._unsplit_value(v) for v in value]
        return super(SeparatedMultipleWidgetMixin, self).get_context(name, value, attrs=attrs, **kwargs)

    def value_from_datadict(self, data, files, name):
        value = super(SeparatedMultipleWidgetMixin, self).value_from_datadict(data, files, name)
        if isinstance(value, (list, tuple)):
            value = [self._split_value(v) for v in value]
        return value


class SeparatedSelect(SeparatedWidgetMixin, Select):

    def _collapse_choices(self, choices):
        for choice in choices:
            if isinstance(choice[0], list):
                choice = (self.token.join([unicode(c) for c in choice[0]]), choice[1])
            yield choice

    def get_context(self, name, value, attrs=None):
        self.choices = list(self._collapse_choices(self.choices))
        return super(SeparatedSelect, self).get_context(name, value, attrs=attrs)


class SeparatedSelectMultiple(SeparatedMultipleWidgetMixin, SelectMultiple):

    def _collapse_choices(self, choices):
        for choice in choices:
            if isinstance(choice[0], list):
                choice = (self.token.join([unicode(c) for c in choice[0]]), choice[1])
            yield choice

    def get_context(self, name, value, attrs=None):
        self.choices = list(self._collapse_choices(self.choices))
        return super(SeparatedSelectMultiple, self).get_context(name, value, attrs=attrs)


class SeparatedTextInput(SeparatedWidgetMixin, TextInput):
    pass


class SeparatedTextarea(SeparatedWidgetMixin, Textarea):
    pass


class SerializedDateTimeInput(DateTimeInput):

    def _format_value(self, value):
        if isinstance(value, six.integer_types):
            value = datetime(value)
        return super(SerializedDateTimeInput, self)._format_value(value)


class MultipleFileInput(FileInput):

    def get_context(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultipleFileInput, self).get_context(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                return value
            else:
                return [value]


class DateTimeRangeInput(NamedMultiWidget):
    pass
