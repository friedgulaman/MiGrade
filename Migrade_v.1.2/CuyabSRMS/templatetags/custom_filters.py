from django import template

register = template.Library()

@register.filter
def num_range(value, end=10):
    return range(value, end + 1)
