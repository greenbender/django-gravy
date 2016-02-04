from django.template import Library, Node
from django.conf import settings
from django.utils import six
from bs4 import BeautifulSoup
register = Library()


import logging
log = logging.getLogger('gravy.templatetags.gravytags')


__all__ = []


class StaticOnceNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    @staticmethod
    def _squash(soup, element='script', source_tag='src'):
        srcs = set()
        for element in soup.find_all(element):
            src = element.get(source_tag)
            if src is None or not src.startswith(settings.STATIC_URL):
                continue
            if src in srcs:
                element.decompose()
                continue
            srcs.add(src)

    def render(self, context):
        output = self.nodelist.render(context)
        soup = BeautifulSoup(output, 'html.parser')
        self._squash(soup, 'script', 'src')
        self._squash(soup, 'link', 'href')
        return str(soup)


class PrettyHtmlNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        soup = BeautifulSoup(output, 'html.parser')
        return soup.prettify(formatter='html')


@register.tag
def staticonce(parser, token):
    """
    Remove duplicate static link and script (CSS and javascript) sources. The
    first reference is kept when a duplicate is found.
    """
    nodelist = parser.parse(('endstaticonce',))
    parser.delete_first_token()
    return StaticOnceNode(nodelist)


@register.tag
def prettyhtml(parser, token):
    """
    Make the html in this tag pretty.
    """
    nodelist = parser.parse(('endprettyhtml',))
    parser.delete_first_token()
    return PrettyHtmlNode(nodelist)


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    dict_ = context['request'].GET.copy()
    for name, value in six.iteritems(kwargs):
        if value is None:
            if name in dict_:
                dict_.pop(name)
        else:
            dict_[name] = value
    return dict_.urlencode()
