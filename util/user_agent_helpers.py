"""
helper methods/utils related to request user agent
"""
from user_agents import parse


def _get_user_agent(request):
    """
    Helper method to get user agent from request
    """
    if not hasattr(request, 'META'):
        return None

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    return parse(ua_string)


def is_mobile_user_agent(request):
    """
    Helper method to check if request user agent is mobile
    """
    user_agent = _get_user_agent(request)
    if user_agent is None:
        return False

    return user_agent.is_mobile


def is_supported_mobile_device(request):
    """
    Helper method to check if request user agent is mobile and is supported
    """
    user_agent = _get_user_agent(request)
    if user_agent is None:
        return False

    return user_agent.is_mobile and user_agent.os.family == 'iOS'


def is_ios(request):
    """
    Helper method to check if request user agent is iOS
    """
    user_agent = _get_user_agent(request)
    if user_agent is None:
        return False

    return user_agent.is_mobile and user_agent.os.family == 'iOS'


def is_android(request):
    """
    Helper method to check if request user agent is Android
    """
    user_agent = _get_user_agent(request)
    if user_agent is None:
        return False

    return user_agent.is_mobile and user_agent.os.family == 'Android'
