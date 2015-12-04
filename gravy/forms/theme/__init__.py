from django.conf import settings
from django.utils.module_loading import import_string
from .base import Theme
from .bootstrap import BootstrapTheme


__all__ = ['Theme', 'BootstrapTheme',]


# apply the theme in settings
theme = getattr(settings, 'FORMS_THEME', None)
if theme is not None:
    import_string(theme).apply_theme()
