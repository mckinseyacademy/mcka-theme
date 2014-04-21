''' API calls with respect to groups '''
from .json_object import JsonParser as JP
from . import group_models
from .json_requests import GET, POST, DELETE

from django.conf import settings

GROUP_API = 'api/groups'

def get_groups():
    ''' gets all groups '''
    response = GET(
        '{}/{}'.format(
            settings.API_MOCK_SERVER_ADDRESS, GROUP_API
        )
    )
    groups_json = JP.from_json(response.read(), group_models.GroupInfo)
    rd = {}
    for group in groups_json:
        rd[group.name] = group.id
    return rd

def create_group(group_name):
    ''' create a new group '''
    response = POST(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS, GROUP_API
        ),
        {"name": group_name,}
    )

    return JP.from_json(response.read(), group_models.GroupInfo)

def fetch_group(group_id):
    ''' fetch group by id '''
    response = GET(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )
    return JP.from_json(response.read(), group_models.GroupInfo)

def delete_group(group_id):
    ''' delete group by id '''
    response = DELETE(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )

    return (response.code == 204)