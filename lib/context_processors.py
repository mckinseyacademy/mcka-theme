import re
from django.conf import settings

from courses.user_courses import standard_data

def user_program_data(request):
    ''' Makes user and program info available to all templates '''
    return standard_data(request)

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

