''' API calls with respect to groups '''
from .json_object import JsonParser as JP
from .json_object import JsonObject
from . import user_models
from . import course_models
from .json_requests import GET, POST, DELETE
from lib.util import DottableDict

from django.conf import settings

GROUP_API = 'api/groups'

PERMISSION_GROUPS = DottableDict(
    MCKA_ADMIN='mcka_role_mcka_admin',
    MCKA_SUBADMIN='mcka_role_mcka_subadmin',
    CLIENT_ADMIN='mcka_role_client_admin',
    CLIENT_SUBADMIN='mcka_role_client_subadmin',
    MCKA_TA='mcka_role_mcka_ta',
    CLIENT_TA='mcka_role_client_ta'
)


def get_groups_of_type(group_type, group_object=JsonObject):
    ''' gets all groups of provided type'''
    response = GET(
        '{}/{}?type={}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_type,
        )
    )

    return JP.from_json(response.read(), group_object)


def create_group(group_name, group_type, group_data=None, group_object=JsonObject):
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


def fetch_group(group_id, group_object=JsonObject):
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

def update_group(group_id, group_type, group_data=None, group_object=JsonObject):
    ''' update existing group '''
    # group_name is fixed, does not get updated, so no need to include it
    data = {
        "group_type": group_type,
    }

    if group_data:
        data["data"] = group_data

    response = POST(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)
    
def add_user_to_group(user_id, group_id, group_object=JsonObject):
    ''' adds user to group '''
    data = {"user_id": user_id}
    response = POST(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


def add_course_to_group(course_id, group_id, group_object=JsonObject):
    ''' adds course to group '''
    data = {"course_id": course_id}
    response = POST(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


def add_group_to_group(child_group_id, group_id, group_object=JsonObject, relationship_type='g'):
    ''' adds user to group '''
    data = {
        "group_id": child_group_id,
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


def get_users_in_group(group_id):
    ''' get list of users associated with a specific group '''
    response = GET(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )

    user_list = JP.from_json(response.read(), user_models.UserList)

    return user_list.users


def get_courses_in_group(group_id):
    ''' get list of courses associated with a specific group '''
    response = GET(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )

    courses_list = JP.from_json(response.read(), course_models.CourseList)

    return courses_list.courses


def get_groups_in_group(group_id, group_object=JsonObject):
    ''' get list of groups associated with a specific group '''
    response = GET(
        '{}/{}/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )

    return JP.from_json(response.read(), group_object)
