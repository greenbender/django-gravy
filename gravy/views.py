from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, CreateView
from django.forms.models import modelform_factory
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View
from django.core.exceptions import PermissionDenied
from datetime import timedelta, datetime
from calendar import timegm


import logging
log = logging.getLogger('gravy.views')


# Create your views here.
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class CsrfExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)


class SuperuserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super(SuperuserRequiredMixin, self).dispatch(request, *args, **kwargs)


class JsonResponseMixin(object):
    def render_to_response(self, context, **kwargs):
        return JsonResponse(self.get_data(context), **kwargs)
    def get_data(self, context):
        return context


class BetterRedirectView(RedirectView):
    permanent = True
    extra_kwargs = {}
    def get_redirect_url(self, *args, **kwargs):
        kwargs.update(self.extra_kwargs)
        return super(BetterRedirectView, self).get_redirect_url(*args, **kwargs)


class NextUrlMixin(object):
    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get('next', '/')
    def get_success_url(self):
        return self.get_redirect_url()


class LastPageBase(object):
    lastpage_namespace = 'lastpage'
    def get_lastpage_key(self, key):
        return ':'.join([
            self.lastpage_namespace,
            key
        ])
        

class LastPageMixin(LastPageBase):
    def get_lastpage_keys(self):
        for key in self.lastpage_keys:
            yield self.get_lastpage_key(key)
    def dispatch(self, request, *args, **kwargs):
        for key in self.get_lastpage_keys():
            request.session[key] = request.path
        return super(LastPageMixin, self).dispatch(request, *args, **kwargs)


class LastPageRedirectView(LastPageBase, BetterRedirectView):
    permanent = False
    lastpage_key = None
    def get_redirect_url(self, *args, **kwargs):
        if self.lastpage_key is not None:
            key = self.get_lastpage_key(self.lastpage_key)
            self.url = self.request.session.get(key)
        return super(LastPageRedirectView, self).get_redirect_url(*args, **kwargs)


class RelatedMixin(object):
    related = ()
    def get_queryset(self):
        qs = super(RelatedMixin, self).get_queryset()
        if self.related and self.request.method in ('GET',):
            qs = qs.select_related(*self.related)
        return qs


class DeferMixin(object):
    """
    Add deferred fields to queryset.
    Note: If you use defer on a DetailView (or any view that uses
    SingleObjectTemplateResponseMixin) the template name will be mangled as a
    proxy model is generated when defer is used.
    Note: This issue #24689 has been patched in django master.
    """
    defer = ()
    def get_queryset(self):
        qs = super(DeferMixin, self).get_queryset()
        if self.defer and self.request.method in ('GET',):
            qs = qs.defer(*self.defer)
        return qs


class AutoSuccessMessageMixin(SuccessMessageMixin):
    def get_success_message(self, cleaned_data):
        if not self.success_message:
            name = self.object.__class__.__name__
            if isinstance(self, CreateView):
                self.success_message = u'%s created successfully.' % name
            elif isinstance(self, UpdateView):
                self.success_message = u'%s updated successfully.' % name
        return super(AutoSuccessMessageMixin, self).get_success_message(cleaned_data)


class ModelFormWidgetMixin(object):
    def get_form_class(self):
        if self.form_class:
            return super(ModelFormWidgetMixin, self).get_form_class()
        if self.model is not None:
            model = self.model
        elif hasattr(self, 'object') and self.object is not None:
            model = self.object.__class__
        else:
            model = self.get_queryset().model
        return modelform_factory(model, fields=self.fields, widgets=self.widgets)


class BulkOperationMixin(object):
    pk_param = 'pk'

    def get_pk_list(self):
        if self.request.method == 'GET':
            return self.request.GET.getlist(self.pk_param)
        elif self.request.method == 'POST':
            return self.request.POST.getlist(self.pk_param)
        return []

    def get_queryset(self):
        pk_list = self.get_pk_list()
        return super(BulkOperationMixin, self).get_queryset().filter(pk__in=pk_list)

    def get_object_list(self):
        pk_list = self.get_pk_list()
        return self.model.objects.filter(pk__in=pk_list)


class ForeignModelMixin(object):
    foreign_context_name = 'foreign'
    foreign_force_query = False
    foreign_required = False

    def get_context_data(self, **kwargs):
        """
        Try to find a model instance to add to the context. Attempts to locate
        an instance efficiently only performing additional queries as a last
        resort.
        """
        context = super(ForeignModelMixin, self).get_context_data(**kwargs)

        # already know the instance
        if self.foreign_object is not None:
            context[self.foreign_context_name] = self.foreign_object
            return context

        # try to find an object from which to grab an instance
        obj = None
        if 'object_list' in context:
            # force evaluation (prevents double query when getting first object)
            obj_list = list(context['object_list'])
            if obj_list:
                obj = obj_list[0]
            context['object_list'] = obj_list
        elif 'object' in context:
            obj = context['object']

        # get the instance from the object when possible
        if obj is not None:
            if isinstance(obj, self.foreign_model):
                self.foreign_object = obj
            elif hasattr(obj, self.foreign_field_name):
                self.foreign_object = getattr(obj, self.foreign_field_name)
            else:
                self.foreign_object = obj[self.foreign_field_name]

        # get the instance from the provided instance pk
        elif self.foreign_object_pk is not None:
            self.foreign_object = get_object_or_404(self.foreign_model, pk=self.foreign_object_pk)

        if self.foreign_object is not None:
            context[self.foreign_context_name] = self.foreign_object

        return context

    def get_form_kwargs(self):
        """
        When a form is posted set the appropriate field to an instance of the
        model when possible.
        """
        kwargs = super(ForeignModelMixin, self).get_form_kwargs()
        if self.foreign_object_pk is not None and 'instance' in kwargs:
            if kwargs['instance'] is None:
                kwargs['instance'] = self.model()
            setattr(kwargs['instance'], self.foreign_field_name + '_id', self.foreign_object_pk)
        return kwargs

    def get_queryset(self):
        """
        Add the model instance to the queryset and filter to instance if given.
        """
        queryset = super(ForeignModelMixin, self).get_queryset()
        if issubclass(queryset.model, self.foreign_model):
            return queryset
        queryset = queryset.select_related(self.foreign_field_name)
        if self.foreign_object_pk is not None:
            filter_kwargs = {self.foreign_field_name + '_id': self.foreign_object_pk}
            queryset = queryset.filter(**filter_kwargs)
        return queryset

    def dispatch(self, request, *args, **kwargs):
        """
        Retreive a model instance pk from get params if it exists. If forced
        also load the instance object from the database.
        """
        self.foreign_object_pk = self.request.GET.get(self.foreign_field_name)
        if self.foreign_required and self.foreign_object_pk is None:
            raise Http404
        if self.foreign_object_pk is not None and self.foreign_force_query:
            self.foreign_object = get_object_or_404(self.foreign_model, pk=self.foreign_object_pk)
        else:
            self.foreign_object = None
        return super(ForeignModelMixin, self).dispatch(request, *args, **kwargs)


class FlotMixin(JsonResponseMixin):

    SECOND = 1
    MINUTE = SECOND * 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    WEEK = DAY * 7

    # helpers
    @staticmethod
    def _datetime(je):
        return timezone.make_aware(
            datetime.utcfromtimestamp(je / 1000), timezone.utc
        )

    @staticmethod
    def _flotutc(dt):
        return timegm(dt.utctimetuple()) * 1000

    @staticmethod
    def _flotutc_sql(expr):
        return 'CAST(EXTRACT(EPOCH FROM %s AT TIME ZONE \'UTC\')*1000 AS BIGINT)' % expr
    
    @classmethod
    def _flotutc_datetime_trunc_sql(cls, lookup_type, field_name):
        return cls._flotutc_sql(
            "DATE_TRUNC('%s', %s AT TIME ZONE \'UTC\')" % (lookup_type, field_name)
        )

    @classmethod
    def _flotwidth(cls, unit):
        ms = 1000
        return {
            'second': cls.SECOND * ms,
            'minute': cls.MINUTE * ms,
            'hour': cls.HOUR * ms,
            'day': cls.DAY * ms,
            'week': cls.WEEK * ms,
        }[unit]

    def get_plot(self, context):
        return {
            'sequence': self.request.GET.get('sequence'),
            'options': {
                'colors': ['#09d809'],
                'series': {
                    'shadowSize': 0,
                    'lines': {'lineWidth': 1},
                    'points': {'lineWidth': 1, 'radius': 2, 'fill': True},
                    'bars': {'lineWidth': 1, 'align': 'center'},
                },
                'grid': {
                    'borderColor': '#eee',
                    'borderWidth': {'top': 0, 'left': 0, 'right': 0, 'bottom': 1},
                    'hoverable': True,
                },
                'zoom': {
                    'interactive': True
                },
                'pan': {
                    'interactive': True
                },
                'xaxis': {
                    'tickLength': 0,
                },
                'yaxis': {
                    'min': 0,
                    'panRange': False,
                    'zoomRange': False,
                    'tickDecimals': 0,
                    'labelWidth': 30,
                    'reserveSpace': True,
                },
            }
        }

    def get_data(self, context):
        return self.get_plot(context)


# TODO: this is a work in progress
class FlotTimeMixin(FlotMixin):
    
    MIN_POINTS = 8

    plot_duration = timedelta(hours=24)
    plot_offsetx = timedelta(hours=1)

    def apply_queryset_limits(self, queryset):

        # extend limits
        delta = self.end - self.begin
        begin = self.begin - delta
        end = self.end + delta

        field = self.plot_fieldx

        # include extra datapoint before limit
        kwargs = {field + '__lt': begin}
        self.before = queryset.values_list(field, flat=True).filter(**kwargs).first()
        if self.before is not None:
            kwargs = {field + '__gte': self.before}
            queryset = queryset.filter(**kwargs)

        # include extra datapoint after limit
        kwargs = {field + '__gt': end}
        self.after = queryset.values_list(field, flat=True).filter(**kwargs).last()
        if self.after is not None:
            kwargs = {field + '__lte': self.after}
            queryset = queryset.filter(**kwargs)

        return queryset

    def get_series(self, context):
        return []

    def get_plot(self, context):
        plot = super(FlotTimeMixin, self).get_plot(context)
        plot['series'] = self.get_series(context)
        plot['options']['xaxis']['min'] = self._flotutc(self.begin)
        plot['options']['xaxis']['max'] = self._flotutc(self.end + self.offsetx)
        plot['options']['xaxis']['mode'] = 'time'
        plot['options']['xaxis']['timezone'] = 'browser'
        plot['options']['xaxis']['zoomRange'] = [1 * 60 * 1000, 4 * 7 * 24 * 60 * 60 * 1000]
        return plot

    def get_unit(self, duration):
        for unit in ('week', 'day', 'hour', 'minute'):
            if duration / self._flotwidth(unit) >= self.MIN_POINTS:
                return unit
        return 'second'

    def get_limits(self):
        # request args
        r = self.request
        self.xmin = int(r.GET['xmin']) if 'xmin' in r.GET else None
        self.xmax = int(r.GET['xmax']) if 'xmax' in r.GET else None
        self.ymin = int(r.GET['ymin']) if 'ymin' in r.GET else None
        self.ymax = int(r.GET['ymax']) if 'ymax' in r.GET else None

        # useful extras
        self.now = timezone.now()
        self.end = self.now if self.xmax is None else self._datetime(self.xmax)
        self.begin = self.end - self.plot_duration if self.xmin is None else self._datetime(self.xmin)
        self.unit = self.get_unit((self.end-self.begin).total_seconds()*1000)
        self.offsetx = self.plot_offsetx if self.xmax is None else timedelta(0)

    def get(self, request, *args, **kwargs):
        self.get_limits()
        return super(FlotTimeMixin, self).get(request, *args, **kwargs)


class FlotPieMixin(FlotMixin):

    def get_plot(self, context):
        plot = super(FlotPieMixin, self).get_plot(context)
        plot['data'] = self.get_series(context)
        plot['options'] = {
            'series': {
                'pie': {
                    'show': True,
                    'radius': 1,
                    'label': {'show': True, 'radius': 0.6},
                    'stroke': {'width': 3},
                }
            },
            'legend': {'show': False}
        }
        return plot


class NullView(View):
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(status=204)
