"""
Core logic to sanitise information for mobile app association views
"""
import os

from django.http import HttpResponse, Http404


def get_app_association_file_response(filename, content_type='application/json'):
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
            response = HttpResponse(android_assets_link_json, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
            return response
    except IOError:
        raise Http404
