from django import template
from django.template.defaultfilters import stringfilter

from courses.controller import get_assessment_module_name_translation

register = template.Library()


@register.filter
@stringfilter
def translate_assessment_if_needed(value):
    """ Translates assessment part of the module name """
    return get_assessment_module_name_translation(value)
