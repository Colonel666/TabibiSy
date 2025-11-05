from django import template

from core.en_ar import EN_AR

register = template.Library()

@register.filter
def tt(value, lang='en'):
    if lang == 'en': return value
    return EN_AR.get(value, value)
