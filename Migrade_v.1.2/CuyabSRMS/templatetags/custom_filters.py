from django import template

register = template.Library()

@register.filter
def num_range(value, end=10):
    return range(value, end + 1)

@register.filter
def num_range_qa(value, end=1):
    return range(value, end + 1)

@register.filter
def th(value, end=13):
    return range(value, end + 1)

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None

@register.filter
def get_value(dictionary, key):
    """
    Custom template filter to retrieve a value from a dictionary.
    """
    return dictionary.get(key, '')

@register.filter
def get_item_rank(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    else:
        return ''
@register.filter(name='replace')
def replace(value, arg):
    """
    Replaces all occurrences of arg in the given string with an empty string.
    """
    return value.replace(arg, '')

@register.filter
def get_dict_keys(dictionary):
    return dictionary.keys()