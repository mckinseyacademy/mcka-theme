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
from . import workgroup_models

PROJECT_API = getattr(settings, 'PROJECT_API', 'api/server/projects')

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
    return project

@api_error_protect
def fetch_project_from_url(url, project_object=JsonObject):
    ''' fetch organization by id '''
    response = GET(url)
    project = JP.from_json(response.read(), project_object)
    return project

@api_error_protect
def delete_project(project_id):
    ''' delete project by id '''
    response = DELETE(
        '{}/{}/{}/'.format(
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
        data["organization"] = organization_id

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

@api_error_protect
def get_project_workgroups(project_id, workgroup_object=workgroup_models.Workgroup):
    response = GET(
        '{}/{}/{}/workgroups/'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            project_id,
        )
    )

    return JP.from_json(response.read(), workgroup_object)
