from django.utils import translation

from accounts.middleware.thread_local import get_current_request


def set_language(language):
    """
    sets language for session
    """
    request = get_current_request()
    if request.LANGUAGE_CODE != language:
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
