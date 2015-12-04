from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import *
from django.forms.fields import *
from django.conf import settings
from django.db.models.fields import TextField
from django.utils import formats
from ..fields import *
from ..widgets import *
from .base import Theme


__all__ = [
    'BootstrapTextInput', 'BootstrapTextarea', 'BootstrapNumberInput',
    'BootstrapSelect', 'BootstrapSeparatedSelect', 'BootstrapDateTimePicker',
    'BootstrapSerializedDateTimePicker', 'BootstrapFileInput',
    'BootstrapCheckboxToggle', 'BootstrapCombobox', 'BootstrapDateRangePicker',
    'BootstrapSeparatedTextarea', 'BootstrapMultipleFileInput',
    'BootstrapTheme',
]


class BootstrapMixin(object):
    classes = None
    toggle = None

    def __init__(self, attrs=None, classes=None, toggle=None, *args, **kwargs):
        if attrs is None:
            attrs = {}
        classes = self.classes if classes is None else classes
        if classes:
            attrs['class'] = ' '.join(classes)
        toggle = self.toggle if toggle is None else classes
        if toggle:
            attrs['data-toggle'] = toggle
        super(BootstrapMixin, self).__init__(attrs=attrs, *args, **kwargs)


class FormControlMixin(object):
    classes = ('form-control',)


class OptionalMixin(object):

    def render(self, name, value, attrs=None):
        if not self.is_required:
            if attrs is None:
                attrs = {}
            attrs['placeholder'] = 'Optional'
        return super(OptionalMixin, self).render(name, value, attrs=attrs)


class BootstrapTextInput(OptionalMixin, FormControlMixin,  BootstrapMixin, TextInput):
    pass
    

class BootstrapTextarea(OptionalMixin, FormControlMixin, BootstrapMixin, Textarea):
    pass


class BootstrapNumberInput(FormControlMixin, BootstrapMixin, NumberInput):
    pass


class BootstrapSelect(FormControlMixin, BootstrapMixin, Select):
    pass


class BootstrapSelectMultiple(FormControlMixin, BootstrapMixin, SelectMultiple):
    pass


class BootstrapSeparatedSelect(FormControlMixin, BootstrapMixin, SeparatedSelect):
    pass


class BootstrapSeparatedTextarea(OptionalMixin, FormControlMixin, BootstrapMixin, SeparatedTextarea):
    pass


class DateTimeMixin(object):
    toggle = 'datetimePicker'

    class Media:
        css = {'all': ('css/bootstrap-datetimepicker.css',)}
        js = (
            'js/moment.min.js',
            'js/bootstrap-datetimepicker.min.js',
            'js/bootstrap.datetimePicker.js',
        )

    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs['data-widget-positioning'] = '{"horizontal": "right", "vertical": "bottom"}'
        attrs['data-format'] = self._moment_format(format or formats.get_format(self.format_key)[0])
        super(DateTimeMixin, self).__init__(attrs=attrs, format=format)

    _format_map = (
        ('DDD', r'%j'),
        ('DD', r'%d'),
        ('MMMM', r'%B'),
        ('MMM', r'%b'),
        ('MM', r'%m'),
        ('YYYY', r'%Y'),
        ('YY', r'%y'),
        ('HH', r'%H'),
        ('hh', r'%I'),
        ('mm', r'%M'),
        ('ss', r'%S'),
        ('a', r'%p'),
        ('ZZ', r'%z'),
    )

    @classmethod
    def _moment_format(cls, fmt):
       for m, d in cls._format_map:
            fmt = fmt.replace(d, m)
       return fmt


class BootstrapDateTimePicker(OptionalMixin, FormControlMixin, DateTimeMixin, BootstrapMixin, DateTimeInput):
    pass


class BootstrapSerializedDateTimePicker(OptionalMixin, FormControlMixin, DateTimeMixin, BootstrapMixin, SerializedDateTimeInput):
    pass


class BootstrapFileInput(OptionalMixin, FormControlMixin, BootstrapMixin, FileInput):
    toggle = 'fileInput'

    class Media:
        css = {'all': ('css/bootstrap.fileInput.css',)}
        js = ('js/bootstrap.fileInput.js',)


class BootstrapCheckboxToggle(BootstrapMixin, CheckboxInput):
    toggle = 'checkboxToggle'

    class Media:
        css = {'all': ('css/bootstrap.checkboxToggle.css',)}
        js = ('js/bootstrap.checkboxToggle.js',)


class BootstrapCombobox(FormControlMixin, BootstrapMixin, Select):
    toggle = 'combobox'

    class Media:
        css = {'all': ('css/bootstrap-combobox.css',)}
        js = (
            'js/bootstrap-combobox.js',
            'js/bootstrap.combobox.js'
        )


class BootstrapDateRangePicker(NamedMultiWidget):
    date_ranges = (
        (1800, '30 min'),
        (3600, '1 hr'),
        (5400, '1.5 hr'),
        (7200, '2 hr'),
    )

    class Media:
        css = {'all': ('css/bootstrap.dateRangePicker.css',)}
        js = ('js/bootstrap.dateRangePicker.js',)

    def __init__(self, date_ranges=None, *args, **kwargs):
        if date_ranges is not None:
            self.date_ranges = date_ranges
        super(BootstrapDateRangePicker, self).__init__(*args, **kwargs)

    def get_date_ranges(self):
        return self.date_ranges

    def format_output(self, rendered_widgets, attrs=None):
        div = '<div data-toggle="dateRangePicker">{0}<div class="btn-group">{1}</div></div>'
        btn = '<button class="btn btn-default" data-value="{0}">{1}</button>'
        btn_group = ''.join([btn.format(v, n) for v, n in self.get_date_ranges()])
        output = super(BootstrapDateRangePicker, self).format_output(rendered_widgets, attrs=attrs)
        return div.format(output, btn_group)


class BootstrapMultipleFileInput(OptionalMixin, FormControlMixin, BootstrapMixin, MultipleFileInput):
    toggle = 'fileInput'

    class Media:
        css = {'all': ('css/bootstrap.fileInput.css',)}
        js = ('js/bootstrap.fileInput.js',)


# XXX: It turns out this was a bad idea as it also modifies the admin
# interface. Make BootstrapFormMixin and BootstrapModelFormMixin instead.
# update: I played around with fixing this but it turns out to be quit a bit
# of work to get it to work correctly ... try again later ... i guess.
class BootstrapTheme(Theme):
    widget_map = (
        (CharField, BootstrapTextInput),
        (BooleanField, BootstrapCheckboxToggle),
        (IntegerField, BootstrapNumberInput),
        (ChoiceField, BootstrapSelect),
        (FileField, BootstrapFileInput),
        (MultipleFileField, BootstrapMultipleFileInput),
        (DateTimeField, BootstrapDateTimePicker),
        (SerializedDateTimeField, BootstrapSerializedDateTimePicker),
        (ModelMultipleChoiceField, BootstrapSelectMultiple),
        (SeparatedChoiceField, BootstrapSeparatedSelect),
    )

    @classmethod
    def apply_theme(cls):
        super(BootstrapTheme, cls).apply_theme()

        # Textarea requires special attention
        _Textarea_render_original = Textarea.render
        def _Textarea_render(self, name, value, attrs=None):
            if attrs is None:
                attrs = {}
            if 'class' in attrs:
                attrs['class'] += ' form-control'
            else:
                attrs['class'] = 'form-control'
            return _Textarea_render_original(self, name, value, attrs=attrs)
        Textarea.render = _Textarea_render
