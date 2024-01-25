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