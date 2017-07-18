"""
helper methods/utils related to request user agent
"""
from user_agents import parse


def is_mobile_user_agent(request):
    """
    Helper method to check if request user agent is mobile
    """
    if not hasattr(request, 'META'):
        return False

    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)

    return user_agent.is_mobile
