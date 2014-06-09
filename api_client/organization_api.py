''' API calls with respect to organizations '''
from django.utils.translation import ugettext as _
from django.conf import settings

from lib.util import DottableDict
from .api_error import api_error_protect, ERROR_CODE_MESSAGES

from .json_object import JsonParser as JP
from .json_object import JsonObject
from .json_requests import GET, POST, DELETE
from . import user_models
from . import course_models


ORGANIZATION_API = 'api/organizations'

PERMISSION_GROUPS = DottableDict(
    MCKA_ADMIN='mcka_role_mcka_admin',
    MCKA_SUBADMIN='mcka_role_mcka_subadmin',
    CLIENT_ADMIN='mcka_role_client_admin',
    CLIENT_SUBADMIN='mcka_role_client_subadmin',
    MCKA_TA='mcka_role_mcka_ta',
    CLIENT_TA='mcka_role_client_ta'
)

@api_error_protect
def create_organization(organization_name, organization_data=None, organization_object=JsonObject):
    ''' create a new organization '''
    data = {
        "name": organization_name,
    }

    if organization_data:
        data["data"] = organization_data

    response = POST(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
        ),
        data
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def fetch_organization(organization_id, organization_object=JsonObject):
    ''' fetch organization by id '''
    response = GET(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    return JP.from_json(response.read(), organization_object)

@api_error_protect
def get_organizations(organization_object=JsonObject):
    ''' fetch all organizations '''
    response = GET(
        '{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
        )
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def delete_organization(organization_id):
    ''' delete organization by id '''
    response = DELETE(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def update_organization(organization_id, organization_data=None, organization_object=JsonObject):
    ''' update existing organization '''
    # organization_name is fixed, does not get updated, so no need to include it
    data = {
        "type": organization_type,
    }

    if organization_data:
        data["data"] = organization_data

    response = POST(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        ),
        data
    )

    return JP.from_json(response.read(), organization_object)

@api_error_protect
def add_user_to_organization(user_id, organization_id, organization_object=JsonObject):
    ''' adds user to organization '''
    data = {"user_id": user_id}
    response = POST(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        ),
        data
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def add_course_to_organization(course_id, organization_id, organization_object=JsonObject):
    ''' adds course to organization '''
    data = {"course_id": course_id}
    response = POST(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        ),
        data
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def add_group_to_organization(child_group_id, organization_id, organization_object=JsonObject, relationship_type='g'):
    ''' adds user to organization '''
    data = {
        "group_id": child_group_id,
        "relationship_type": relationship_type
    }
    response = POST(
        '{}/{}/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        ),
        data
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def get_users_in_organization(organization_id):
    ''' get list of users associated with a specific organization '''
    response = GET(
        '{}/{}/{}/users'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    user_list = JP.from_json(response.read(), user_models.UserList)

    return user_list.users

@api_error_protect
def remove_user_from_organization(organization_id, user_id):
    ''' remove user association with a specific organization '''

    response = DELETE(
        '{}/{}/{}/users/{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
            user_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def get_courses_in_organization(organization_id):
    ''' get list of courses associated with a specific organization '''
    response = GET(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    courses_list = JP.from_json(response.read(), course_models.CourseListCourse)

    return courses_list


@api_error_protect
def get_groups_in_organization(organization_id, organization_object=JsonObject, params=[]):

    paramStrs = [param['key'] + '=' + param['value'] for param in params]
    if len(paramStrs) > 0:
        paramStr = '&'.join(paramStrs)
    else:
        paramStr = ''

    ''' get list of groups associated with a specific organization '''

    response = GET(
        '{}/{}/{}/groups?{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
            paramStr
        )
    )

    return JP.from_json(response.read(), organization_object)

ORGANIZATION_ERROR_CODE_MESSAGES = {
    create_organization: {
        403: _("Permission Denied"),
        401: _("Invalid data"),
    },
    update_organization: {
        403: _("Permission Denied"),
        401: _("Invalid data"),
    },
}
ERROR_CODE_MESSAGES.update(ORGANIZATION_ERROR_CODE_MESSAGES)
