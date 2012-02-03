from django import template

register = template.Library()

@register.filter
def class_name(obj, arg=None):
    """
    Filter to return object's class name using Python's built-in constants
    """
    # Any object
    try:
        if hasattr(obj.__class__, '__name__'):
            return obj.__class__.__name__.lower()
    except AttributeError, e:
        pass

    # Queryset object
    try:
        if hasattr(obj.model, '__name__'):
            return obj.model.__name__.lower()
    except AttributeError, e:
        pass

    # Form object
    try:
        if hasattr(obj.Meta.model, '__name__'):
            return obj.Meta.model.__name__.lower()
    except AttributeError, e:
        pass