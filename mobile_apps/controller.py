"""
Core logic to sanitise information for mobile_apps app views
"""
import os

from django.http import HttpResponse, Http404

from util.user_agent_helpers import is_supported_mobile_device, is_ios, is_android
from api_client import user_api
from api_client import mobileapp_api
from api_client.api_error import ApiError

from .constants import (
    APP_DOWNLOAD_BANNER_IMAGES,
    MOBILE_APP_DEPLOYMENT_MECHANISMS,
    COMPANIES_MOBILE_APPS_MAP
)


def get_app_association_file_response(filename):
    """
    Helper method to get app association json file response
    """
    asset_links_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'asset_links_files',
        filename
    )
    try:
        with open(asset_links_file_path) as asset_links_file:
            android_assets_link_json = asset_links_file.read()
            response = HttpResponse(android_assets_link_json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
            return response
    except IOError:
        raise Http404


def has_mobile_ready_course(user_id):
    """
    Returns boolean based on if user has any mobile ready course
    """
    qs_params = dict(mobile_only=True)
    # TODO:  Request a dedicated API to get if user has a mobile-ready course
    #        and use that API instead of using progress api.
    response = user_api.get_user_courses_progress(user_id, qs_params)

    return True if response else False


def get_mobile_app_download_popup_data(request):
    """
    Returns mobile app data for to be displayed on download popup
    """
    popup_data = dict()
    try:
        users = user_api.get_users(username=request.GET['username'])
        if users and has_mobile_ready_course(users[0].id):
            companies = user_api.get_user_organizations(users[0].id)
            if companies:
                popup_data['company_mobile_app_map'] = build_company_mobileapp_popup_data(
                    request,
                    companies[0].id
                )
    except ApiError:
        pass

    if is_supported_mobile_device(request) and'company_mobile_app_map' in popup_data \
            and popup_data['company_mobile_app_map']:
        popup_data['show_app_link_popup'] = True

    return popup_data


def build_company_mobileapp_popup_data(request, company_id):
    """
    Returns dict containing mobile app data for the specified company
    """
    popup_data = dict()
    mobileapps = mobileapp_api.get_mobile_apps(dict(organization_ids=company_id))['results']
    if len(mobileapps) == 1 and mobileapps[0]['is_active'] and company_id in COMPANIES_MOBILE_APPS_MAP:
        popup_data = COMPANIES_MOBILE_APPS_MAP[company_id]
        mobile_app = mobileapps[0]
        if is_ios(request) and mobile_app.get('ios_download_url'):
            popup_data['ios'] = mobile_app.get('ios_download_url')
            popup_data['mobile_device'] = 'ios'
            if mobile_app.get('deployment_mechanism') == MOBILE_APP_DEPLOYMENT_MECHANISMS['public_store']:
                popup_data['download_banner_image'] = APP_DOWNLOAD_BANNER_IMAGES['ios_store']
        elif is_android(request) and mobile_app.get('android_download_url'):
            popup_data['android'] = mobile_app.get('android_download_url')
            popup_data['mobile_device'] = 'android'
            if mobile_app.get('deployment_mechanism') == MOBILE_APP_DEPLOYMENT_MECHANISMS['public_store']:
                popup_data['download_banner_image'] = APP_DOWNLOAD_BANNER_IMAGES['android_store']
        else:
            return dict()

    return popup_data
