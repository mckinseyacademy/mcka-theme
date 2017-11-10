"""
Views for Mobile App Associations djangoapp.
"""
from .controller import get_app_association_file_response


def android_asset_links_file(request): # pylint: disable=unused-argument
    """
    View to return asset links file for android app verification
    """
    return get_app_association_file_response('assetlinks.json')

def ios_site_association_file(request): # pylint: disable=unused-argument
    """
    View to return iOS app association file
    """
    return get_app_association_file_response('apple-app-site-association')
