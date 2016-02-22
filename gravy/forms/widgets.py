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
    'SeparatedWidgetMixin', 'SeparatedSelect', 'SeparatedTextInput',
    'SeparatedTextarea', 'SerializedDateTimeInput', 'MultipleFileInput',
    'DateTimeRangeInput', 'DependsWidget',
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

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
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
            widget_name = self.subwidget_name_format.format(name, widget_name)
            output.append(widget.render(widget_name, widget_value, widget_attrs))
        return mark_safe(self.format_output(output, attrs=final_attrs))

    def id_for_label(self, id_):
        return id_

    def value_from_datadict(self, data, files, name):
        value = []
        for widget_name, widget in six.iteritems(self.named_widgets):
            widget_name = self.subwidget_name_format.format(name, widget_name)
            value.append(widget.value_from_datadict(data, files, widget_name))
        return value

    def format_output(self, rendered_widgets, attrs=None):
        final_attrs = {'class': self.classname}
        id_ = attrs.get('id')
        if id_:
            final_attrs['id'] = id_
        rendered = []
        hidden = []
        for i, subwidget in enumerate(self.named_widgets.items()):
            widget_name, widget = subwidget
            if widget.is_hidden:
                hidden.append(rendered_widgets[i])
            else:
                label = self._labels.get(widget_name, '')
                if label:
                    label_attrs = {}
                    title = self._help_texts.get(widget_name)
                    if title:
                        label_attrs['title'] = title
                    label = format_html('<label {}>{}</label>', flatatt(label_attrs), label)
                rendered.append(format_html('<li>{}{}</li>', label, rendered_widgets[i]))
        return format_html('<ul {}>{}{}</ul>',
            flatatt(final_attrs),
            mark_safe(''.join(hidden)),
            mark_safe(''.join(rendered))
        )

    def decompress(self, value):
        if value:
            return [value.get(name, None) for name in self.named_widgets.keys()]
        return [None]*len(self.named_widgets)


# TODO: cleanup rendering attrs etc
class RepeatNamedMultiWidget(NamedMultiWidget):

    widget_class = 'repeat-named-multi-widget'
    toggle = 'repeatNamedMultiWidget'

    class Media:
        css = {
            'all': ('css/jquery.repeatNamedMultiWidget.css',)
        }
        js = ('js/jquery.repeatNamedMultiWidget.js',)

    _id_fmt = ' id="{id}"'
    _ul_fmt = '<ul{id} class="{classname}" data-toggle="{toggle}" data-repeat-template="{template}">{subwidgets}<span class="{classname}-add"></span></ul>'
    _li_fmt = '<li><span class="{classname}-remove"></span>{subwidget}</li>'
    _nin_re = re.compile(r'(?P<name>[^\[]+)\[(?P<index>\d+)\](?P<next>.*)')

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

    def render(self, name, values, attrs=None):
        name += '[]'
        final_attrs = self.build_attrs(attrs)
        widget_attrs = dict(final_attrs)
        widget_attrs.pop('id', None)
        template_value = self._initial
        if not isinstance(values, list):
            template_value, values = values, []
        template = super(RepeatNamedMultiWidget, self).render(name, template_value, widget_attrs)
        rendered_widgets = []
        for i, value in enumerate(values):
            rendered_widgets.append(super(RepeatNamedMultiWidget, self).render(name, value, widget_attrs))
        return mark_safe(self.format_output_repeat(template, rendered_widgets, attrs=final_attrs))

    def format_output_repeat(self, template, rendered_widgets, attrs=None):
        if self.is_hidden:
            return ''.join(rendered_widgets)
        id_ = attrs.get('id')
        id_ = self._id_fmt.format(id=id_) if id_ else ''
        template = escape(self._li_fmt.format(classname=self.widget_class, subwidget=template))
        rendered = []
        for i, rendered_widget in enumerate(rendered_widgets):
            rendered.append(self._li_fmt.format(classname=self.widget_class, subwidget=rendered_widget))
        return self._ul_fmt.format(classname=self.widget_class,
            toggle=self.toggle, id=id_, template=template,
            subwidgets=''.join(rendered)
        )


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

    def render(self, name, value, attrs=None):
        if isinstance(value, dict):
            split = [value.get(n) for n in self.attribute_map]
            value = urlparse.urlunsplit(split)
        return super(ParsedURLInput, self).render(name, value, attrs=attrs)


class SeparatedWidgetMixin(object):

    def __init__(self, attrs=None, token=',', cleanup=True, **kwargs):
        self.token = token
        self.cleanup = cleanup
        super(SeparatedWidgetMixin, self).__init__(attrs=attrs, **kwargs)

    def render(self, name, value, attrs=None, **kwargs):
        if isinstance(value, list):
            value = self.token.join([unicode(v) for v in value])
        return super(SeparatedWidgetMixin, self).render(name, value, attrs=attrs, **kwargs)

    def value_from_datadict(self, data, files, name):
        value = super(SeparatedWidgetMixin, self).value_from_datadict(data, files, name)
        if not isinstance(value, six.string_types):
            return value
        values = value.split(self.token)
        if self.cleanup:
            values = filter(bool, [v.strip() for v in values])
        return values


class SeparatedSelect(SeparatedWidgetMixin, Select):

    def _collapse_choices(self, choices):
        for choice in choices:
            if isinstance(choice[0], list):
                choice = (self.token.join([unicode(c) for c in choice[0]]), choice[1])
            yield choice

    def render(self, name, value, attrs=None, choices=()):
        choices = list(self._collapse_choices(choices))
        self.choices = list(self._collapse_choices(self.choices))
        return super(SeparatedSelect, self).render(name, value, attrs=attrs, choices=choices)


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

    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultipleFileInput, self).render(name, value, attrs)

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
