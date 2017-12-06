"""This file include all the controller methods."""
from accounts import controller
from api_client import user_api


def get_android_app_manifest_json(user_id):
    """
    Returns json data with user_android_mobile_app_id and name to show android native app banner
    """
    name = None
    user_android_mobile_app_id = None
    organization_id = None
    icon_src = None

    organizations = user_api.get_user_organizations(user_id)

    if len(organizations) > 0:

        data = controller.get_mobile_apps_id(organizations[0])

        organization_id = organizations[0].id
        name = data['org_name']
        user_android_mobile_app_id = data['android_app_id']

    if organization_id == 17:
        icon_src = "/static/image/mcka_banner_logo.png"
    elif organization_id == 153:
        icon_src = "/static/image/rtsa_banner_logo.png"

    manifest_json = {
        "name": name,
        "short_name": name,
        "icons": [
            {
                "src": icon_src,
                "type": "image/png",
                "sizes": "192x192"
            }
        ],
        "related_applications": [
            {
                "platform": "play",
                "id": user_android_mobile_app_id
            }
        ],
    }

    return manifest_json
