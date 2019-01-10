''' API calls with respect to groups '''
from django.utils.translation import ugettext as _
from django.conf import settings
from urllib import urlencode

from lib.utils import DottableDict
from .api_error import api_error_protect, ERROR_CODE_MESSAGES
from api_data_manager.group_data import GROUP_PROPERTIES
from api_data_manager.user_data import USER_PROPERTIES
from api_data_manager.common_data import COMMON_DATA_PROPERTIES
from api_data_manager.signals import (
    user_data_updated,
    group_data_updated,
    common_data_updated,
)
from api_data_manager.decorators import group_api_cache_wrapper

from .json_object import JsonParser as JP
from .json_object import JsonObject
from .json_requests import GET, POST, DELETE
from . import user_models
from . import course_models


GROUP_API = getattr(settings, 'GROUP_API', 'api/server/groups')

PERMISSION_TYPE = 'permission'

PERMISSION_GROUPS = DottableDict(
    MCKA_ADMIN='mcka_role_mcka_admin',
    MCKA_SUBADMIN='mcka_role_mcka_subadmin',
    MCKA_TA='mcka_role_mcka_ta',
    MCKA_OBSERVER='mcka_role_mcka_observer',
    CLIENT_ADMIN='mcka_role_client_admin',
    CLIENT_SUBADMIN='mcka_role_client_subadmin',
    CLIENT_TA='mcka_role_client_ta',
    CLIENT_OBSERVER='mcka_role_client_observer',
    INTERNAL_ADMIN='mcka_role_internal_admin',
    COMPANY_ADMIN='mcka_role_company_admin',
    MANAGER='manager',
    MODERATOR='instructor'
)

TAG_GROUPS = DottableDict(
    INTERNAL='tag:internal',
    COMMON='tag',
)


@api_error_protect
def get_groups_of_type(group_type, group_object=JsonObject, *args, **kwargs):
    ''' gets all groups of provided type'''

    qs_params = {
        "page_size": 0,
        "type": group_type,
    }

    for karg in kwargs:
        if isinstance(kwargs[karg], list):
            qs_params[karg] = ",".join(kwargs[karg])
        else:
            qs_params[karg] = kwargs[karg]

    response = GET(
        '{}/{}/?{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            urlencode(qs_params),
        )
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def create_group(group_name, group_type, group_data=None, group_object=JsonObject):
    ''' create a new group '''
    data = {
        "name": group_name,
        "type": group_type,
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


@api_error_protect
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


@api_error_protect
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


@api_error_protect
def update_group(group_id, group_name, group_type, group_data=None, group_object=JsonObject):
    ''' update existing group '''
    data = {
        "type": group_type,
        "name": group_name
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


@api_error_protect
def add_users_to_group(user_ids, group_id, group_object=JsonObject):
    ''' adds user to group '''

    # trigger event that data is updated for this user
    user_data_updated.send(
        sender=__name__, user_ids=user_ids,
        data_type=USER_PROPERTIES.GROUPS
    )
    user_ids = ','.join(map(str, user_ids))
    data = {"user_id": user_ids}
    response = POST(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
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

    # trigger event that data is updated for this group
    group_data_updated.send(
        sender=__name__, group_ids=[group_id],
        data_type=GROUP_PROPERTIES.COURSES
    )

    # trigger event as program-course-mapping is updated
    common_data_updated.send(
        sender=__name__,
        data_type=COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING,
        data_changed={'group_id': group_id}
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
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


@api_error_protect
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


@api_error_protect
def remove_user_from_group(user_id, group_id):
    ''' remove user association with a specific group '''

    # trigger event that data is updated for this user
    user_data_updated.send(
        sender=__name__, user_ids=[user_id],
        data_type=USER_PROPERTIES.GROUPS
    )

    response = DELETE(
        '{}/{}/{}/users/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
            user_id,
        )
    )

    return response.code == 204


@api_error_protect
def remove_course_from_group(course_id, group_id, group_object=JsonObject):
    ''' removes course from group '''

    response = DELETE(
        '{}/{}/{}/courses/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
            course_id,
        )
    )

    # trigger event that data is updated for this group
    group_data_updated.send(
        sender=__name__, group_ids=[group_id],
        data_type=GROUP_PROPERTIES.COURSES
    )

    # trigger event as program-course-mapping is updated
    common_data_updated.send(
        sender=__name__,
        data_type=COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING,
        data_changed={'group_id': group_id}
    )

    return response.code == 204


@api_error_protect
@group_api_cache_wrapper(
    parse_method=JP.from_json,
    parse_object=course_models.CourseListCourse,
    property_name=GROUP_PROPERTIES.COURSES
)
def get_courses_in_group(group_id):
    ''' get list of courses associated with a specific group '''
    response = GET(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
        )
    )

    return response.read()


@api_error_protect
def get_groups_in_group(group_id, group_object=JsonObject, *args, **kwargs):
    ''' get list of groups associated with a specific group '''

    qs_params = {}
    qs_params.update(kwargs)
    response = GET(
        '{}/{}/{}/groups?{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
            urlencode(qs_params),
        )
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def get_organizations_in_group(group_id, group_object=JsonObject):
    response = GET(
        '{}/{}/{}/organizations/'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id
        )
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def get_workgroups_in_group(group_id, group_object=JsonObject):
    response = GET(
        '{}/{}/{}/workgroups/?page_size=0'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id
        )
    )

    return JP.from_json(response.read(), group_object)


GROUP_ERROR_CODE_MESSAGES = {
    "create_group": {
        403: _("Permission Denied"),
        401: _("Invalid data"),
    },
    "update_group": {
        403: _("Permission Denied"),
        401: _("Invalid data"),
    },
}
ERROR_CODE_MESSAGES.update(GROUP_ERROR_CODE_MESSAGES)
