''' API calls with respect to groups '''
from django.utils.translation import ugettext as _
from django.conf import settings
from urllib import urlencode

from lib.utils import DottableDict
from .api_error import api_error_protect, ERROR_CODE_MESSAGES

from .json_object import JsonParser as JP
from .json_object import JsonObject
from .json_requests import GET, POST, DELETE, PUT
from . import user_models
from . import course_models
from . import workgroup_models

PROJECT_API = getattr(settings, 'PROJECT_API', 'api/server/projects')


def get_project_url_by_id(project_id):
    return '{}/{}/{}/'.format(
        settings.API_SERVER_ADDRESS,
        PROJECT_API,
        project_id,
    )


@api_error_protect
def get_project(project_id, project_object=JsonObject):
    ''' fetch project by id '''
    response = GET(get_project_url_by_id(project_id))

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

    return response.code == 204


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
def get_all_projects(course_id=None, content_id=None, project_object=JsonObject):
    ''' update existing project '''

    qs_params = {}
    if course_id and content_id:
        qs_params["course_id"]=course_id
        qs_params["content_id"]=content_id
    response = GET(
        '{}/{}?{}'.format(
            settings.API_SERVER_ADDRESS,
            PROJECT_API,
            urlencode(qs_params),
        ),
    )

    return JP.from_json(response.read(), project_object).results


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
