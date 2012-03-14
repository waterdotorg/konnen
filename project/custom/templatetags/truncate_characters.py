from django import template
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy

register = template.Library()

@register.filter
def truncate_characters(s, num, end_text='...'):
    """
    Truncates a string after a certain number of characters. Takes an optional
    argument of what should be used to notify that the string has been
    truncated, defaulting to ellipsis (...)

    Newlines in the string will be stripped.
    """
    s = force_unicode(s)
    length = int(num)
    if len(s) > length:
        s = s[:length]
        if not s[-3:].endswith(end_text):
            s = s + end_text
    return s
truncate_characters = allow_lazy(truncate_characters, unicode)