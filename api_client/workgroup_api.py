''' API calls with respect to groups '''
from django.utils.translation import ugettext as _
from django.conf import settings

from lib.util import DottableDict
from .api_error import api_error_protect, ERROR_CODE_MESSAGES

from .json_object import JsonParser as JP
from .json_object import JsonObject
from .json_requests import GET, POST, DELETE
from . import user_models
from . import course_models


WORKGROUP_API = 'api/workgroups'

PERMISSION_GROUPS = DottableDict(
    MCKA_ADMIN='mcka_role_mcka_admin',
    MCKA_SUBADMIN='mcka_role_mcka_subadmin',
    CLIENT_ADMIN='mcka_role_client_admin',
    CLIENT_SUBADMIN='mcka_role_client_subadmin',
    MCKA_TA='mcka_role_mcka_ta',
    CLIENT_TA='mcka_role_client_ta'
)

@api_error_protect
def get_workgroups(group_object=JsonObject):
    ''' gets all workgroups'''
    response = GET(
        '{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
        )
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_workgroup(workgroup_id, group_object=JsonObject):
    ''' fetch workgroup by id '''
    response = GET(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        )
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def delete_workgroup(workgroup_id):
    ''' delete workgroup by id '''
    response = DELETE(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def create_workgroup(workgroup_name, workgroup_data=None, group_object=JsonObject):
    ''' create a new workgroup '''
    data = {
        "name": workgroup_name,
    }

    if workgroup_data:
        data = workgroup_data

    response = POST(
        '{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def update_workgroup(workgroup_id, workgroup_data=None, group_object=JsonObject):
    ''' update existing workgroup '''
    data = {}

    if workgroup_data:
        data["data"] = workgroup_data

    response = POST(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def add_user_to_workgroup(user_id, workgroup_id, group_object=JsonObject):
    ''' adds user to workgroup '''
    data = {"user_id": user_id}
    response = POST(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def get_users_in_workgroup(workgroup_id):
    ''' get list of users associated with a specific workgroup '''
    response = GET(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        )
    )

    user_list = JP.from_json(response.read(), user_models.UserList)

    return user_list.users

@api_error_protect
def remove_user_from_workgroup(workgroup_id, user_id):
    ''' remove user association with a specific workgroup '''

    response = DELETE(
        '{}/{}/{}/users/{}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
            user_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def add_workgroup_to_group(workgroup_id, group_id, group_object=JsonObject, relationship_type='g'):
    ''' adds workgroup to group '''
    data = {
        "workgroup_id": workgroup_id,
        "relationship_type": relationship_type
    }
    response = POST(
        '{}/{}/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_groups(workgroup_id, group_object=JsonObject):
    ''' get groups attached to workgroup '''

    response = GET(
        '{}/{}/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        )
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_groups_by_type(workgroup_id, group_type, group_object=JsonObject):
    ''' get groups attached to workgroup '''

    response = GET(
        '{}/{}/{}/groups?type={}'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
            group_type,
        )
    )

    return JP.from_json(response.read(), group_object)
