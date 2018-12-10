from django.utils import translation, six
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.conf import settings

from accounts.middleware.thread_local import get_current_request


def set_language(language=settings.LANGUAGE_CODE):
    """
    sets language for session
    """
    language_supported = [lang for lang in settings.LANGUAGES if lang[0] == language]
    language = language if language_supported else settings.LANGUAGE_CODE
    request = get_current_request()
    if request.LANGUAGE_CODE != language:
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language


def _format_lazy(format_string, *args, **kwargs):
    """
    Apply str.format() on 'format_string' where format_string, args,
    and/or kwargs might be lazy.
    """
    return format_string.format(*args, **kwargs)


# TODO: format_lazy was introduced in Django 1.11, remove this after upgrade to django 1.11
format_lazy = lazy(_format_lazy, six.text_type)
mark_safe_lazy = lazy(mark_safe, six.text_type)
