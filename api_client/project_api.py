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

# Temporary id converter to fix up problems post opaque keys
from lib.util import LegacyIdConvert


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
def get_project(project_id, project_object=JsonObject):
    ''' fetch project by id '''
    response = GET(
        '{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        )
    )

    project = JP.from_json(response.read(), project_object)
    course_id = project.course_id
    project.course_id = LegacyIdConvert.new_from_legacy(project.course_id, course_id)
    project.content_id = LegacyIdConvert.new_from_legacy(project.content_id, course_id)

    return project

@api_error_protect
def fetch_project_from_url(url, project_object=JsonObject):
    ''' fetch organization by id '''
    response = GET(url)
    project = JP.from_json(response.read(), project_object)
    course_id = project.course_id
    project.course_id = LegacyIdConvert.new_from_legacy(project.course_id, course_id)
    project.content_id = LegacyIdConvert.new_from_legacy(project.content_id, course_id)

    return project

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
def create_project(course_id, content_id, organization_id=None, project_object=JsonObject):
    ''' create a new project '''
    data = {
        "course_id": course_id,
        "content_id": content_id,
    }

    if not organization_id is None:
        data["organization_id"] = organization_id

    response = POST(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
        ),
        data
    )

    return JP.from_json(response.read(), project_object)


@api_error_protect
def update_project(project_id, project_data, project_object=JsonObject):
    ''' update existing project '''

    response = PUT(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        ),
        project_data
    )

    return JP.from_json(response.read(), project_object)
