''' API calls with respect to groups '''
from .json_object import JsonParser as JP
from . import group_models
from .json_requests import GET, POST, DELETE

from django.conf import settings

GROUP_API = 'api/groups'


def get_groups(group_object=group_models.GroupInfo):
    ''' gets all groups '''
    response = GET(
        '{}/{}'.format(
            settings.API_MOCK_SERVER_ADDRESS,
            GROUP_API,
        )
    )
    groups_json = JP.from_json(response.read(), group_object)
    rd = {}
    for group in groups_json:
        rd[group.name] = group.id
    return rd


def get_groups_of_type(group_type, group_object=group_models.GroupInfo):
    ''' gets all groups of provided type'''
    response = GET(
        '{}/{}?type={}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_type,
        )
    )
    return JP.from_json(response.read(), group_object)


def create_group(group_name, group_type, group_data=None, group_object=group_models.GroupInfo):
    ''' create a new group '''
    data = {
        "name": group_name,
        "group_type": group_type,
    }

    if group_data:
        data["data"] = group_data

    response = POST(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


def fetch_group(group_id, group_object=group_models.GroupInfo):
    ''' fetch group by id '''
    response = GET(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )
    return JP.from_json(response.read(), group_object)


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
