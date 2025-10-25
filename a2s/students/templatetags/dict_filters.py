from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get dictionary value safely in template"""
    return d.get(key)
