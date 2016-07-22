from django.forms.fields import *
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.core.files.storage import DefaultStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from ..utils import epoch
from .widgets import *
from betterforms.forms import BetterForm, Fieldset
from collections import OrderedDict
import urlparse
import jsonschema
import json
import copy
import six
import re


import logging
log = logging.getLogger('gravy.forms.fields')


__all__ = [
    'NamedMultiValueField', 'RepeatNamedMultiValueField', 'SavedFileField',
    'ParsedURLField', 'SerializedDateTimeField',
    'SerializedModelMultipleChoiceField', 'ModelChoiceLabelMixin',
    'ModelChoiceAltLabelField', 'ModelMultipleChoiceAltLabelField',
    'SerializedModelMultipleChoiceAltLabelField', 'SeparatedFieldMixin',
    'SeparatedChoiceField', 'SeparatedMultipleChoiceField',
    'SeparatedCharField', 'FilePermissionsField', 'DateTimeRangeField',
    'SerializedDateTimeRangeField', 'MultipleFileField', 'SchemaParseError',
    'validate_json', 'FormGenerator', 'normalise_schema', 'form_from_schema',
    'FieldsetMixin', 'FieldsetFormGenerator', 'fieldsetform_from_schema',
    'fieldsetform_from_schemas', 'FormSchemaField', 'FieldsetFormSchemaField',
    'DependsField',
]

# proxy django.forms.fields
import django.forms.fields
__all__.extend(django.forms.fields.__all__)
# proxy .widgets
import widgets
__all__.extend(widgets.__all__)


# TODO: the whole labels, help_texts, initial thing could be changed a bit
class NamedMultiValueField(MultiValueField):
    widget = NamedMultiWidget
    fields = ()

    def __init__(self, fields=None, widget_kwargs=None, *args, **kwargs):
        kwargs.setdefault('require_all_fields', False)
        self.named_fields = OrderedDict(fields or self.fields)
        widgets, initial, help_texts, labels = OrderedDict(), {}, {}, {}
        for name, field in six.iteritems(self.named_fields):
            widgets[name] = field.widget
            if hasattr(field, 'initial'):
                initial[name] = field.initial
            if hasattr(field, 'label'):
                labels[name] = field.label
            if hasattr(field, 'help_text'):
                help_texts[name] = field.help_text
        if widget_kwargs is None:
            widget_kwargs = {}
        widget = self.widget(
            widgets=widgets,
            labels=labels,
            help_texts=help_texts,
            initial=initial,
            **widget_kwargs
        )
        fields = self.named_fields.values()
        super(NamedMultiValueField, self).__init__(
            widget=widget, fields=fields, initial=initial,
            *args, **kwargs
        )

    def compress(self, data_list):
        return dict(zip(self.named_fields.keys(), data_list))


# TODO: add ability to set intial number of repetitions
class RepeatNamedMultiValueField(NamedMultiValueField):
    widget = RepeatNamedMultiWidget

    def clean(self, value):
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return [super(RepeatNamedMultiValueField, self).clean(v) for v in value]


class DependsField(BooleanField):
    widget = DependsWidget


class SavedFileField(FileField):
    """
    A FileField that saves the file using the supplied storage. The field value
    is the filename of the saved file.
    """
    storage_class = DefaultStorage

    def get_storage(self):
        return self.storage_class()

    def save(self, value):
        return self.get_storage().save(value.name, value)

    def to_python(self, value):
        value = super(SavedFileField, self).to_python(value)
        if value in self.empty_values:
            return None
        return self.save(value)


class SerializedDateTimeField(DateTimeField):
    """
    A DateTimeField that serializes the returned date.
    """
    widget = SerializedDateTimeInput

    def to_python(self, value):
        value = super(SerializedDateTimeField, self).to_python(value)
        if value in self.empty_values:
            return None
        return epoch(value)


class DateTimeRangeField(NamedMultiValueField):
    widget = DateTimeRangeInput
    datetime_field_class = DateTimeField
    default_error_messages = {
        'invalid_datetime': _('Enter a valid datetime.'),
        'negative_range'  : _('Start time is after end time.'),
    }

    def __init__(self, input_formats=None, require_start=False, require_end=False, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        localize = kwargs.get('localize', False)
        fields = (
            ('start', self.datetime_field_class(
                label='Start',
                input_formats=input_formats,
                required=require_start,
                error_messages={'invalid': errors['invalid_datetime']},
                localize=localize,
            )),
            ('end', self.datetime_field_class(
                label='End',
                input_formats=input_formats,
                required=require_end,
                error_messages={'invalid': errors['invalid_datetime']},
                localize=localize,
            )),
        )
        super(DateTimeRangeField, self).__init__(fields=fields, *args, **kwargs)

    def clean(self, value):
        cleaned = super(DateTimeRangeField, self).clean(value)
        if 'start' in cleaned and 'end' in cleaned and cleaned['start'] > cleaned['end']:
            raise ValidationError(self.error_messages['negative_range'])
        return cleaned


class SerializedDateTimeRangeField(DateTimeRangeField):
    datetime_field_class = SerializedDateTimeField


class SerializedModelMultipleChoiceField(ModelMultipleChoiceField):

    def clean(self, value):
        qs = super(SerializedModelMultipleChoiceField, self).clean(value)
        return [object.pk for object in qs]


class ModelChoiceLabelMixin(object):
    label_attr = None
    def label_from_instance(self, obj):
        if self.label_attr is not None:
            return getattr(obj, self.label_attr)
        return super(ModelChoiceLabelMixin, self).label_form_instance(obj)


class ModelChoiceAltLabelField(ModelChoiceLabelMixin, ModelChoiceField):
    pass


class ModelMultipleChoiceAltLabelField(ModelChoiceLabelMixin, ModelMultipleChoiceField):
    pass


class SerializedModelMultipleChoiceAltLabelField(ModelChoiceLabelMixin, SerializedModelMultipleChoiceField):
    pass


class FilePermissionsField(CharField):
    default_validators = [
        MinValueValidator(0),
        MaxValueValidator(0777),
    ]

    default_error_messages = {
        'invalid': _('Enter a whole number.') 
    }

    def to_python(self, value):
        value = super(FilePermissionsField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            value = int(value, 0)
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class ParsedURLField(URLField):
    widget = ParsedURLInput
    attribute_map = (
        'scheme',
        'netloc',
        'path',
        'query',
        'fragment',
        'username',
        'password',
        'hostname',
        'port'
    )
    default_ports = {
        'http': 80,
        'https': 443,
    }

    def clean(self, value):
        fullurl = value = super(ParsedURLField, self).clean(value)
        if value:
            # we know is it sane because URLField says so
            split = urlparse.urlsplit(value)
            value = dict([(n, getattr(split, n, None)) for n in self.attribute_map])
            # always try to set the port
            if value['port'] is None:
                value['port'] = self.default_ports.get(value['scheme'])
            # add a full path - since its useful
            fullpath = value['path']
            if value['query']:
                fullpath += '?' + value['query']
            fullpath += value['fragment']
            value['fullpath'] = fullpath
            value['fullurl'] = fullurl
        return value


class SeparatedFieldMixin(object):
    def to_python(self, value):
        if isinstance(value, list):
            return [super(SeparatedFieldMixin, self).to_python(v) for v in value]
        return super(SeparatedFieldMixin, self).to_python(value)


class SeparatedChoiceField(SeparatedFieldMixin, ChoiceField):
    widget = SeparatedSelect


class SeparatedMultipleChoiceField(SeparatedFieldMixin, MultipleChoiceField):
    widget = SeparatedSelectMultiple


# TODO: add validation that it is a list etc
class SeparatedCharField(SeparatedFieldMixin, CharField):
    widget = SeparatedTextInput


class MultipleFileField(FileField):
    widget = MultipleFileInput

    def to_python(self, value):
        return [super(MultipleFileField, self).to_python(v) for v in value]


class SchemaParseError(ValueError):
    def __init__(self, message, context=None):
        super(SchemaParseError, self).__init__(message)
        self.context = context

    @property
    def schema(self):
        if self.context is None:
            return ''
        if isinstance(self.context, six.string_types):
            return self.context
        return json.dumps(self.context, indent=4)

    @property
    def html(self):
        return format_html('{}<br><pre>{}</pre>', self.message, self.schema)


def validate_json(obj, schema, **kwargs):
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.ValidationError as e:
        message = kwargs.get('message', e.message)
        context = kwargs.get('context', obj)
        raise SchemaParseError(message, context)


class FormGenerator(object):
    """
    Parses a form fields schema to actual form fields. When parsing issues are
    encountered a SchemaParseError is raised (when subclassing this methodology
    should continue to be used).
    """
    def __init__(self, fields, validate=True):
        if validate:
            self.validate(fields)
        self.__fields = fields

    def get_form_class(self):
        self.formfields = OrderedDict()
        for field in self.__fields:
            # ignore empty fields
            if field:
                self.formfields[field['name']] = self.create_field(field)
        return type('DynamicForm', (BetterForm,), self.formfields)

    @classmethod
    def validate(cls, fields):
        validate_json(fields, {'type': 'array'})
        for field in fields:
            # ignore empty fields
            if field:
                cls.validate_field(field)

    @staticmethod
    def get_field_options(field):
        options = {}
        options['label'] = field.get('label', '')
        options['help_text'] = field.get('help_text')
        options['required'] = field.get('required', False)
        if 'initial' in field:
            options['initial'] = field['initial']
        if field.get('hidden', False):
            options['widget'] = HiddenInput
        return options

    @classmethod
    def validate_field_options(cls, field):
        schema = {
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'help_text': {'type': 'string'},
                'required': {'type': 'boolean'},
                'hidden': {'type': 'boolean'}
            }
        }
        validate_json(field, schema)
        return cls.get_field_options(field)

    def create_field(self, field):
        options = self.get_field_options(field)
        return getattr(self, 'create_field_for_' + field['type'])(field, options)

    @classmethod
    def validate_field(cls, field):
        options = cls.validate_field_options(field)
        schema = {
            'type': 'object',
            'properties': {
                'type': {'type': 'string'}
            }, 'required': ['type']
        }
        validate_json(field, schema)
        if not hasattr(cls, 'create_field_for_' + field['type']):
            raise SchemaParseError('The field type "%s" is not supported.' % field['type'], field)
        func = getattr(cls, 'validate_field_for_' + field['type'], None)
        if func is not None:
            func(field, options)

    @staticmethod
    def create_field_for_text(field, options):
        options['max_length'] = field.get('max_length', 20)
        return CharField(**options)

    @staticmethod
    def validate_field_for_text(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['text']},
                'initial': {'type': 'string'},
                'max_length': {'type': 'integer', 'minimum': 0}
            }, 'required': ['type']
        }
        validate_json(field, schema)

    @staticmethod
    def create_field_for_file(field, options):
        options['max_length'] = field.get('max_length', 512)
        return SavedFileField(**options)

    @staticmethod
    def validate_field_for_file(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['file']},
                'initial': {'type': 'string'},
                'max_length': {'type': 'integer', 'minimum': 0}
            }, 'required': ['type']
        }
        validate_json(field, schema)

    @staticmethod
    def create_field_for_textarea(field, options):
        options['max_length'] = field.get('max_length', 9999)
        return CharField(widget=Textarea(attrs={'rows': '5'}), **options)

    @staticmethod
    def validate_field_for_textarea(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['textarea']},
                'initial': {'type': 'string'},
                'max_length': {'type': 'integer', 'minimum': 0}
            }, 'required': ['type']
        }
        validate_json(field, schema)

    @staticmethod
    def create_field_for_integer(field, options):
        options['min_value'] = field.get('min_value', -999999999)
        options['max_value'] = field.get('max_value', 999999999)
        return IntegerField(**options)

    @staticmethod
    def validate_field_for_integer(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['integer']},
                'initial': {'type': 'integer'},
                'min_value': {'type': 'integer'},
                'max_value': {'type': 'integer'}
            }, 'required': ['type']
        }
        validate_json(field, schema)
        if field.get('min_value', -999999999) > field.get('max_value', 999999999):
            raise SchemaParseError('min_value must be less than or equal to max_value.', field)

    @staticmethod
    def create_field_for_datetime(field, options):
        return DateTimeField(**options)

    @staticmethod
    def validate_field_for_datetime(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['datetime']},
                'initial': {'type': 'string'}
            }, 'required': ['type']
        }
        validate_json(field, schema)

    @staticmethod
    def create_field_for_perm(field, options):
        return FilePermissionsField(**options)

    @staticmethod
    def validate_field_for_perm(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['perm']},
                'initial': {'type': 'integer'}
            }, 'required': ['type']
        }
        validate_json(field, schema)

    @staticmethod
    def create_field_for_radio(field, options):
        options['choices'] = [(c['value'], c['name']) for c in field['choices']]
        return ChoiceField(widget=RadioSelect, **options)

    @staticmethod
    def validate_field_for_radio(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['radio']},
                'choices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'value': {},
                        }, 'required': ['name', 'value']
                    }
                }
            }, 'required': ['type', 'choices']
        }
        validate_json(field, schema)
        sentinel = object()
        initial = field.get('initial', sentinel)
        if initial is not sentinel and initial not in [c['value'] for c in field['choices']]:
            raise SchemaParseError('initial must match one of the values given in choices.', field)

    @staticmethod
    def create_field_for_select(field, options):
        options['choices'] = [(c['value'], c['name']) for c in field['choices']]
        return ChoiceField(**options)

    @staticmethod
    def validate_field_for_select(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['select']},
                'choices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'value': {},
                        }, 'required': ['name', 'value']
                    }
                }
            }, 'required': ['type', 'choices']
        }
        validate_json(field, schema)
        sentinel = object()
        initial = field.get('initial', sentinel)
        if initial is not sentinel and initial not in [c['value'] for c in field['choices']]:
            raise SchemaParseError('initial must match one of the values given in choices.', field)

    @staticmethod
    def create_field_for_selectlist(field, options):
        options['choices'] = [(c['value'], c['name']) for c in field['choices']]
        return SeparatedChoiceField(**options)

    @staticmethod
    def validate_field_for_selectlist(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['selectlist']},
                'choices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'value': {'type': 'array'},
                        }, 'required': ['name', 'value']
                    }
                }
            }, 'required': ['type', 'choices']
        }
        validate_json(field, schema)
        sentinel = object()
        initial = field.get('initial', sentinel)
        if initial is not sentinel and initial not in [c['value'] for c in field['choices']]:
            raise SchemaParseError('initial must match one of the values given in choices.', field)

    @staticmethod
    def create_field_for_multipleselect(field, options):
        options['choices'] = [(c['value'], c['name']) for c in field['choices']]
        return MultipleChoiceField(**options)

    @staticmethod
    def validate_field_for_multipleselect(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['multipleselect']},
                'initial': {'type': 'array'},
                'choices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'value': {},
                        }, 'required': ['name', 'value']
                    }
                }
            }, 'required': ['type', 'choices']
        }
        validate_json(field, schema)
        initial = field.get('initial', [])
        for v in initial:
            if v not in  [c['value'] for c in field['choices']]:
                raise SchemaParseError('initial must be a subset the values given in choices.', field)

    @staticmethod
    def create_field_for_multipleselectlist(field, options):
        options['choices'] = [(c['value'], c['name']) for c in field['choices']]
        return SeparatedMultipleChoiceField(**options)

    @staticmethod
    def validate_field_for_multipleselectlist(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['multipleselectlist']},
                'initial': {'type': 'array'},
                'choices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'value': {'type': 'array'},
                        }, 'required': ['name', 'value']
                    }
                }
            }, 'required': ['type', 'choices']
        }
        validate_json(field, schema)
        initial = field.get('initial', [])
        for v in initial:
            if v not in  [c['value'] for c in field['choices']]:
                raise SchemaParseError('initial must be a subset the values given in choices.', field)

    @staticmethod
    def create_field_for_checkbox(field, options):
        return BooleanField(**options)

    @staticmethod
    def validate_field_for_checkbox(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['checkbox']},
                'initial': {'type': 'boolean'},
            }, 'required': ['type']
        }
        validate_json(field, schema)

    @staticmethod
    def create_field_for_enable(field, options):
        return DependsField(**options)

    @staticmethod
    def validate_field_for_enable(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['enable']},
                'initial': {'type': 'boolean'},
            }, 'required': ['type']
        }
        validate_json(field, schema)

    def create_field_for_multiple(self, field, options):
        options['fields'] = []
        for subfield in field['fields']:
            # ignore empty subfields
            if subfield:
                options['fields'].append((subfield['name'], self.create_field(subfield)))
        return NamedMultiValueField(**options)

    @classmethod
    def validate_field_for_multiple(cls, field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['multiple']},
                'fields': {'type': 'array'}
            }, 'required': ['type', 'fields']
        }
        validate_json(field, schema)
        for subfield in field['fields']:
            # ignore empty subfields
            if subfield:
                cls.validate_field(subfield)

    def create_field_for_repeat(self, field, options):
        options['fields'] = []
        for subfield in field['fields']:
            # ignore empty subfields
            if subfield:
                options['fields'].append((subfield['name'], self.create_field(subfield)))
        return RepeatNamedMultiValueField(**options)

    @classmethod
    def validate_field_for_repeat(cls, field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['repeat']},
                'fields': {'type': 'array'}
            }, 'required': ['type', 'fields']
        }
        validate_json(field, schema)
        for subfield in field['fields']:
            # ignore empty subfields
            if subfield:
                cls.validate_field(subfield)

    @staticmethod
    def create_field_for_url(field, options):
        options['max_length'] = field.get('max_length', 4096)
        return ParsedURLField(**options)

    @staticmethod
    def validate_field_for_url(field, options):
        schema = {
            'type': 'object',
            'properties': {
                'type': {'enum': ['url']},
                'initial': {'type': 'string'},
                'max_length': {'type': 'integer', 'minimum': 0}
            }, 'required': ['type']
        }
        validate_json(field, schema)


def normalise_schema(schema):
    if hasattr(schema, 'read'):
        schema = schema.read()
    if isinstance(schema, six.string_types):
        try:
            normalised_schema = json.loads(schema)
        except ValueError as e:
            raise SchemaParseError(e, schema)
        return normalised_schema
    # since the schema may be modified we need a copy
    return copy.deepcopy(schema)


def form_from_schema(schema, generator_class=FormGenerator, validate=True):
    """
    Accepts a form schema in string, fileobject or list format, normalises it
    and returns a form class that reflects the suppiled schema.

    Raises a ValueError with the appropriate message the schema is invalid.
    """
    normalised_schema = normalise_schema(schema)
    generator = generator_class(normalised_schema, validate=validate)
    return generator.get_form_class()


class FieldsetMixin(object):
    """
    Mixin to tranparently handle the namespacing that is added by the fieldset
    form generator. It adds an additional dictionary level to cleaned_data and
    reformats namespacing for intial. See FieldsetFormGenerator.create_field()
    """
    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs and kwargs['initial']:
            initial = {}
            for fieldset_name, fieldset in six.iteritems(kwargs['initial']):
                for field_name, value in six.iteritems(fieldset):
                    name = '.'.join([fieldset_name, field_name])
                    initial[name] = value
            kwargs['initial'] = initial
        super(FieldsetMixin, self).__init__(*args, **kwargs)

    @cached_property
    def cleaned_fieldset_data(self):
        cleaned = {}
        for name, value in six.iteritems(self.cleaned_data):
            fieldset_name, field_name = name.split('.', 1)
            if not fieldset_name in cleaned:
                cleaned[fieldset_name] = {}
            cleaned[fieldset_name][field_name] = value
        return cleaned


class FieldsetFormGenerator(FormGenerator):
    """
    Parses a fieldset form fields schema to actual form fields and formsets.
    When parsing issues are encountered a SchemaParseError is raised (when
    subclassing this methodology should continue to be used).
    """
    def __init__(self, fieldsets, validate=True):
        if validate:
            self.validate(fieldsets)
        self.__fieldsets = fieldsets

    def get_form_class(self):
        self.formfields = OrderedDict()
        self.fieldsets = []
        for fieldset in self.__fieldsets:
            # ignore empty fieldsets
            if fieldset:
                self.fieldsets.append(self.create_fieldset(fieldset))
        class Meta:
            fieldsets = tuple(self.fieldsets)
        self.formfields['Meta'] = Meta
        return type('DynamicFieldsetForm', (FieldsetMixin, BetterForm,), self.formfields)

    @classmethod
    def validate(cls, fieldsets):
        validate_json(fieldsets, {'type': 'array'})
        for fieldset in fieldsets:
            # ignore empty fieldsets
            if fieldset:
                cls.validate_fieldset(fieldset)

    @staticmethod
    def get_fieldset_options(fieldset):
        options = {}
        options['legend'] = fieldset['legend']
        options['help_text'] = fieldset.get('help_text')
        options['is_hidden'] = fieldset.get('hidden', False)
        return options

    @staticmethod
    def validate_fieldset_options(fieldset):
        schema = {
            'type': 'object',
            'properties': {
                'legend': {'type': 'string'},
                'help_text': {'type': 'string'},
                'hidden': {'type': 'boolean'}
            }, 'required': ['legend']
        }
        validate_json(fieldset, schema)

    def create_fieldset(self, fieldset):
        options = self.get_fieldset_options(fieldset)
        options['fields'] = []
        for field in fieldset['fields']:
            # namespace field name with fieldset name
            field['name'] = '.'.join([fieldset['name'], field['name']])
            f = self.create_field(field)
            self.formfields[field['name']] = f
            options['fields'].append(field['name'])
        options['fields'] = tuple(options['fields'])
        fs = Fieldset(fieldset['name'], **options)
        return fs

    @classmethod
    def validate_fieldset(cls, fieldset):
        cls.validate_fieldset_options(fieldset)
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'fields': {'type': 'array'}
            }, 'required': ['name', 'fields']
        }
        validate_json(fieldset, schema)
        for field in fieldset['fields']:
            cls.validate_field(field)


def _merge_fields(a, b):
    a.extend(b)
    return a


def _merge_fieldset(a, b):
    for k, v in six.iteritems(b):
        if k == 'fields':
            _merge_fields(a[k], b[k])
        else:
            a[k] = v
    return a


def _merge_schema(a, b):
    e = []
    for bf in b:
        bd = False
        for i, af in enumerate(a):
            if af['name'] == bf['name']:
                _merge_fieldset(af, bf)
                bd = True
        if not bd:
            e.append(bf)
    a.extend(e)
    return a


def fieldsetform_from_schema(schema, generator_class=FieldsetFormGenerator, validate=True):
    """
    Accepts a fieldset form schema in string, fileobject or list format,
    normalises it and returns a form class that reflects the suppiled schema.

    Raises a ValueError with the appropriate message the schema is invalid.
    """
    return form_from_schema(schema, generator_class=generator_class, validate=validate)


def fieldsetform_from_schemas(*schemas, **kwargs):
    """
    Accepts one or more fieldset form schemas in string, fileobject or list
    format, normalises and merges them into a single schema and returns a form
    class that reflects the merged schema.

    The order of the fieldsets in the merged schema is first in best dressed
    i.e. fieldsets in the first schema will be first in the merged schema and
    so on.

    The legend and description of a fieldset will be overwritten by each schema
    that defines a fieldset with the same name (later schemas overriding
    earlier schemas).

    Fields can be added to a fieldset (or overwritten) by each schema that
    defines a fieldset with the same name (later schemas overriding earlier
    schemas).

    Raises a ValueError with the appropriate message any of the schemas are
    invalid.
    """
    generator_class = kwargs.get('generator_class', FieldsetFormGenerator)
    normalised_schemas = map(normalise_schema, schemas)
    # validate the schemas before merge
    for normalised_schema in normalised_schemas:
        generator_class.validate(normalised_schema)
    merged = reduce(_merge_schema, normalised_schemas, [])
    return fieldsetform_from_schema(merged, generator_class=generator_class, validate=False)


class FormSchemaField(CharField):
    """
    A field for entering a form schema and having it validated and returned as
    a django form.
    """
    widget = Textarea
    default_error_messages = {
        'invalid': _('Not a valid schema: %(schema)s')
    }
    generator_class = FormGenerator

    def __init__(self, *args, **kwargs):
        generator_class = kwargs.pop('generator_class', None)
        if generator_class is not None:
            self.generator_class = generator_class
        super(FormSchemaField, self).__init__(*args, **kwargs)

    def get_form(self, value):
        return form_from_schema(value, generator_class=self.generator_class)

    def to_python(self, value):
        value = super(FormSchemaField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            return self.get_form(value)
        except SchemaParseError as e:
            raise ValidationError(self.error_messages['invalid'], code='invalid', params={'schema': e.schema})


class FieldsetFormSchemaField(FormSchemaField):
    """
    A field for entering a fieldset form schema and having it validated and
    returned as a django form.
    """
    generator_class = FieldsetFormGenerator

    def get_form(self, value):
        return fieldsetform_from_schema(value,
            generator_class=self.generator_class
        )
