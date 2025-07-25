import markdown
from django import template
from django.contrib.staticfiles import finders
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_str as force_unicode
from django.utils.safestring import mark_safe
from core.settings.utils import absolute_path

register = template.Library()


@register.filter("klass")
def klass(ob):
    return ob.__class__.__name__


@register.filter(name='base_markdown', is_safe=True)
@stringfilter
def base_markdown(value):
    extensions = ["nl2br", "markdown.extensions.tables", "fenced_code"]
    html_output = markdown.markdown(
        force_unicode(value),
        extensions=extensions,
        safe_mode=True,
        enable_attributes=False)
    # html_output = html_output.replace(
    #     '<table>', '<p><table>').replace(
    #         '</table>', '</table></p>')
    return mark_safe(html_output)


@register.filter(name='is_gif', is_safe=True)
@stringfilter
def is_gif(value):
    return value[-4:] == '.gif'


@register.filter
def local_static_filepath(value):
    """It gives the local filepath of a static file.

    Inspired by:
    https://stackoverflow.com/questions/9391167/django-how-to-get-a-static-
    files-filepath-in-a-development-environment

    :param value: The name of the static file to look for.

    :return: The local file path.
    """
    return finders.find(value)


@register.filter
def to_char(value):
    """Return a letter according to the number given.

    Eg 1 is returning "a".
    """
    return chr(96 + value)


@register.inclusion_tag('button_span.html', takes_context=True)
def show_button_icon(context, value):

    context_icon = {
        'add': 'glyphicon glyphicon-asterisk',
        'update': 'glyphicon glyphicon-pencil',
        'delete': 'glyphicon glyphicon-minus',
        'back': 'glyphicon glyphicon-arrow-left'
    }

    return {
        'button_icon': context_icon[value]
    }


@register.filter
def columns(thelist, n):
    """
    Break a list into ``n`` columns, filling up each column to the maximum
    equal length possible. For example::
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n
    if list_len % n != 0:
        split += 1
    return [thelist[i::split] for i in range(split)]


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag(takes_context=True)
def version_tag(context):
    """Reads current project release from the .version file."""
    version_file = absolute_path('.version')
    try:
        with open(version_file, 'r') as file:
            version = file.read()
            context['version'] = version
    except IOError:
        context['version'] = 'Unknown'
    return context['version']
