import re
import logging
from django.conf import settings

import geoip2.database
from geoip2.errors import AddressNotFoundError

from courses.user_courses import standard_data
from courses.models import FeatureFlags

from edx_notifications.server.web.utils import get_notifications_widget_context
from util.user_agent_helpers import is_mobile_user_agent, is_ios, is_android
from lib.utils import find_maxmind_database, get_client_ip_address


log = logging.getLogger(__name__)
max_mind_reader = geoip2.database.Reader(find_maxmind_database())


def add_edx_notification_context(data):
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

    data = get_notifications_widget_context(data)

    return data


def user_program_data(request):
    ''' Makes user and program info available to all templates '''

    course_name = None

    data = standard_data(request)

    # add in edx-notifications context
    data = add_edx_notification_context(data)

    if 'course' in data and data['course']:
        if data['course'].id:
            (features, created) = FeatureFlags.objects.get_or_create(course_id=data['course'].id)

            course_name = data['course'].name

            data.update({
                'namespace': data['course'].id,
                'feature_flags': features,
            })

    data.update({
        'course_name': course_name,
    })

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
        "xblock_theme_css_path": settings.XBLOCK_THEME_CSS_PATH,
    }

    return data


def mobile_login_data(request):
    """
    Make mobile login data available to all templates
    """
    data = dict()
    if is_mobile_user_agent(request) and request.META.get('HTTP_REFERER')\
            and '/login/' in request.META.get('HTTP_REFERER'):
        if is_android(request):
            data['track_mobile_login'] = 'Android'
        elif is_ios(request):
            data['track_mobile_login'] = 'iOS'

    return data


def set_mobile_app_id(request):
    """
    Make android and ios app id available to all templates
    """
    data = dict()
    if is_mobile_user_agent(request):
        if is_android(request):
            data['user_organization_id'] = request.COOKIES.get('user_organization_id')
            data['user_android_mobile_app_id'] = request.COOKIES.get('android_app_id')
        elif is_ios(request):
            data['user_ios_mobile_app_id'] = request.COOKIES.get('ios_app_id')

    return data


def geolocate_ip_address(request):
    """
    Geo-Locates the IP Address from a request.
    :param request: A request object.
    :return: Returns a dictionary of 'country_code' to the 2 digit country code
    for the resulting country. Example: China = 'CN'
    """
    data = {}
    country_code = request.session.get('country_code', None)
    if country_code:
        data['country_code'] = country_code
        return data
    country_code = None
    ip_address = get_client_ip_address(request)
    if ip_address:
        try:
            response = max_mind_reader.country(ip_address)
        except AddressNotFoundError:
            # This is likely a local IP Address.
            response = None
        if response:
            country_code = response.country.iso_code
    request.session['country_code'] = country_code
    data['country_code'] = country_code
    return data
