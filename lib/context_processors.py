import re
from django.conf import settings

from courses.user_courses import standard_data

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
                "poll_period_secs": 10,
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
            data.update({
                'namespace': data['course'].id
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

