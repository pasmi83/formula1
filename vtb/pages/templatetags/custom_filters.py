from django import template

register = template.Library()

@register.filter
def value_from_key(value,key):
    print('%%%%%',value,key)
    attr=getattr(value,key)
    return attr