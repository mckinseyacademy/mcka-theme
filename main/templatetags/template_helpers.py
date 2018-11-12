from django.conf import settings
from django import template

register = template.Library()


@register.filter
def template_fragment_cache_timeouts(fragment_name):
    """
    Returns cache timeout values for passed template fragment
    """
    cache_timeouts = settings.CACHE_TIMEOUTS.get('template_fragments', {})
    return cache_timeouts.get(fragment_name, 0)
