# __init__.py

from django import template

register = template.Library()

from . import custom_filters
