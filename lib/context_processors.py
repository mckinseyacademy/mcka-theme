import re
from django.conf import settings

from courses.user_courses import standard_data
from courses.models import FeatureFlags

from edx_notifications.server.web.utils import get_notifications_widget_context

import logging

log = logging.getLogger(__name__)

def user_program_data(request):
    ''' Makes user and program info available to all templates '''

    data = standard_data(request)

    # add in edx-notifications context
    data.update({
        "refresh_watcher": {
            "name": "short-poll",
            "args": {
                "poll_period_secs": 30,
            }
        },
        "global_variables": {
            # we only selectively want dates in the unread
            # pane
            "always_show_dates_on_unread": False,
            "hide_link_is_visible": False,
        },
        "view_audios": {
            # no audio alert for now
            "notification_alert": None,
        },
    })

    if 'course' in data and data['course']:
        if data['course'].id:
            (features, created) = FeatureFlags.objects.get_or_create(course_id=data['course'].id)

            data.update({
                'namespace': data['course'].id,
                'feature_flags': features,
            })
    data = get_notifications_widget_context(data)

    return data

def settings_data(request):
    ''' makes global settings available to all templates '''
    ie_favicon_prefix = ""
    if request.META.has_key('HTTP_USER_AGENT'):
        ua = request.META['HTTP_USER_AGENT'].lower()
        if re.search('msie ', ua):
            ie_favicon_prefix = "{}://{}".format(
                "https" if request.is_secure() else "http",
                request.META['HTTP_HOST'],
            )
            if re.search('msie [1-8]\.', ua):
                request.is_IE8 = True

    data = {
        "ga_tracking_id": settings.GA_TRACKING_ID,
        "ta_email_group": settings.TA_EMAIL_GROUP,
        "ie_favicon_prefix": ie_favicon_prefix,
        "session_id": request.session.session_key,
        "mapbox_token": settings.MAPBOX_API['public_token'],
        "mapbox_map_id": settings.MAPBOX_API['map_id'],
        "apros_features": settings.FEATURES,
    }

    return data

def google_analytics(request):
    """
    Use the variables returned in this function to
    render your Google Analytics tracking code template.
    """
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_PROPERTY_ID', False)
    ga_domain = getattr(settings, 'GOOGLE_ANALYTICS_DOMAIN', False)
    if not settings.DEBUG and ga_prop_id and ga_domain:
        return {
            'GOOGLE_ANALYTICS_PROPERTY_ID': 'UA-77644470-1',
            'GOOGLE_ANALYTICS_DOMAIN': '54.221.197.82',
        }
    return {}
