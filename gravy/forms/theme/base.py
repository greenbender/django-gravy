import sys

__all__ = ['Theme',]


import logging
log = logging.getLogger('gravy.forms.theme.base')


class Theme(object):
    widget_map = ()

    @classmethod
    def get_widget_map(cls):
        return cls.widget_map

    @classmethod
    def apply_theme(cls):
        for field, widget in cls.get_widget_map():
            field.widget = widget
