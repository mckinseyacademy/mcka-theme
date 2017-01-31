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


WORKGROUP_API = getattr(settings, 'WORKGROUP_API', 'api/server/workgroups')

@api_error_protect
def get_workgroups(group_object=JsonObject):
    ''' gets all workgroups'''
    response = GET(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
        )
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_workgroups_for_project(project_id):
    ''' gets all workgourps for a specific project_id'''
    return [wg for wg in get_workgroups() if wg.project == project_id]


@api_error_protect
def get_workgroup(workgroup_id, group_object=JsonObject):
    ''' fetch workgroup by id '''
    response = GET(
        '{}/{}/{}/'.format(
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
        '{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def create_workgroup(workgroup_name, workgroup_data, group_object=JsonObject):
    ''' create a new workgroup '''

    data = workgroup_data
    data["name"] = workgroup_name

    response = POST(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
        ),
        data
    )

    return JP.from_json(response.read(), group_object)


@api_error_protect
def update_workgroup(workgroup_id, workgroup_data, group_object=JsonObject):
    ''' update existing workgroup '''
    response = PATCH(
        '{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
        workgroup_data
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def add_user_to_workgroup(workgroup_id, user_id):
    response = POST(
        '{}/{}/{}/users/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
        {"id": user_id}
    )

    return (response.code == 201)

@api_error_protect
def remove_user_from_workgroup(workgroup_id, user_id):
    response = DELETE(
        '{}/{}/{}/users/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
        {"id": user_id}
    )

    return (response.code == 204)

@api_error_protect
def get_workgroup_users(workgroup_id, group_object=JsonObject):
    response = GET(
        '{}/{}/{}/users/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def add_group_to_workgroup(workgroup_id, group_id):
    response = POST(
        '{}/{}/{}/groups/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
        {"id": group_id}
    )

    return (response.code == 201)

@api_error_protect
def get_workgroup_groups(workgroup_id, group_object=JsonObject):
    response = GET(
        '{}/{}/{}/groups/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        ),
    )

    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_workgroup_submissions(workgroup_id, submission_object=JsonObject):
    response = GET(
        '{}/{}/{}/submissions/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id,
        )
    )

    return JP.from_json(response.read(), submission_object)

def get_latest_workgroup_submissions_by_id(workgroup_id, submission_object=JsonObject):
    submission_list = get_workgroup_submissions(workgroup_id, submission_object)

    submissions_by_id = {}
    for submission in submission_list:
        submission_id = submission.document_id
        if submission_id in submissions_by_id:
            if submission.modified > submissions_by_id[submission_id].modified:
                submissions_by_id[submission_id] = submission
        else:
            submissions_by_id[submission_id] = submission

    return submissions_by_id

@api_error_protect
def get_workgroup_review_items(workgroup_id):
    response = GET(
        '{}/{}/{}/workgroup_reviews/'.format(
            settings.API_SERVER_ADDRESS,
            WORKGROUP_API,
            workgroup_id
        )
    )
    return JP.from_json(response.read())


@api_error_protect
def get_groupwork_activity(uri):
    response = GET(uri)
    return JP.from_json(response.read())
