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


PROJECT_API = 'api/projects'

PERMISSION_GROUPS = DottableDict(
    MCKA_ADMIN='mcka_role_mcka_admin',
    MCKA_SUBADMIN='mcka_role_mcka_subadmin',
    CLIENT_ADMIN='mcka_role_client_admin',
    CLIENT_SUBADMIN='mcka_role_client_subadmin',
    MCKA_TA='mcka_role_mcka_ta',
    CLIENT_TA='mcka_role_client_ta'
)

@api_error_protect
def get_projects(group_object=JsonObject):
    ''' gets all projects'''
    response = GET(
        '{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
        )
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_project(project_id, group_object=JsonObject):
    ''' fetch project by id '''
    print '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        )
    response = GET(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        )
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def delete_project(project_id):
    ''' delete project by id '''
    response = DELETE(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def create_project(project_name, project_data=None, group_object=JsonObject):
    ''' create a new project '''
    data = {
        "name": project_name,
    }

#    if project_data:
#       data["data"] = project_data

    response = POST(
        '{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def update_project(project_id, project_data=None, group_object=JsonObject):
    ''' update existing project '''
    data = {}

    if project_data:
        data["data"] = project_data

    response = POST(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)
