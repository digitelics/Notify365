from django import template

register = template.Library()

@register.filter(name='replace_underscore_with_space')
def replace_underscore_with_space(value):
    return value.replace('_', ' ')
