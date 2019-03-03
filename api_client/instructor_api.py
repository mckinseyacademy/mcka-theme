"""
Calls to edx-platform instructor REST API.
"""
from django.conf import settings

from .api_error import api_error_protect

from api_client.oauth2_requests import get_oauth2_session

BASE_URI = getattr(settings, 'INSTRUCTOR_API', 'api/instructor/v1')
COURSE_INSTRUCTOR_URI = '{server_address}/{base_uri}/course'.format(
    server_address=settings.API_SERVER_ADDRESS,
    base_uri=BASE_URI,
)
INSTRUCTOR_TASKS_URI = '{server_address}/{base_uri}/tasks'.format(
    server_address=settings.API_SERVER_ADDRESS,
    base_uri=BASE_URI,
)


@api_error_protect
def generate_problem_responses_report(course_id, problem_locations):
    """Create answer report for a specific course.

    Args:

        course_id (str): Course Id.
        problem_locations (list): List of strings for one or more problem_locations.

    Returns:
        :str: Celery task id.
    """
    edx_oauth2_session = get_oauth2_session()
    url = '{base_uri}/{course_id}/reports/problem_responses'.format(
            base_uri=COURSE_INSTRUCTOR_URI,
            course_id=course_id
    )
    params = {'problem_location': ','.join(problem_locations)}
    response = edx_oauth2_session.post(url, data=params)
    return response.json()


@api_error_protect
def list_tasks(course_id, problem_location=None):
    """List pending tasks for a specific course.

    'Tasks' mean Celery tasks. Usually these tasks corresponds to reports being constructed.

    Args:
        param (str) course_id: Course Id.
        param (str, optional) problem_location: Problem location.

    Returns:
        list: lists of task's details.
    """
    edx_oauth2_session = get_oauth2_session()
    response = edx_oauth2_session.post(
        '{base_uri}/{course_id}/tasks'.format(
            base_uri=COURSE_INSTRUCTOR_URI,
            course_id=course_id
        ),
        data={'problem_location': problem_location}
    )
    return response.json()['tasks']


@api_error_protect
def get_report_downloads(course_id, report_name=None):
    """Retrieve available report downloads.

    After a report is done this function can be used to discover the files available for download.

    Args:
        course_id (str): Course Id.
        report_name (str, optional): Report Name.

    Returns:
        list: List of dictionaries with downloads' details..
    """
    edx_oauth2_session = get_oauth2_session()

    if report_name is not None:
        params = {'report_name': report_name}
    else:
        params = {}

    response = edx_oauth2_session.post(
        '{base_uri}/{course_id}/reports'.format(
            base_uri=COURSE_INSTRUCTOR_URI,
            course_id=course_id
        ),
        data=params
    )
    return response.json()['downloads']


@api_error_protect
def get_task_status(task_id, *task_ids):
    """Retrieve status of one or more instructor tasks.

    Give multiple task ids to retrieve statuses for multiple tasks

    Note:
        For more information on the response checkout `lms.djangoapps.instrutor_task.views.instructor_task_status`

    Args:
        task_id (str): task id.

    Return:
        dict: Task details.

    Examples:
        >>> get_task_status('task_id')  # Retrieve status for one task.
        ... {'task_id': 'task_id', 'task_progress': 'RUNNING', ...}
        >>> get_task_status('task_id', 'task_id2', 'task_id3')  # Retrieve status for multiple tasks.
        ... { 'task_id1': { 'task_id': 'task_id1', 'task_progress': 'RUNNING' },
        ... 'task_id2': { 'task_id': 'task_id2', 'task_progress': 'DONE' },
        ... 'task_id3': { 'task_id': 'task_id3', 'task_progress': 'RUNNING' } }
    """
    edx_oauth2_session = get_oauth2_session()

    if not len(task_ids):
        payload = {'task_id': task_id}
    else:
        payload = {'task_ids': ','.join([task_id] + task_ids)}

    response = edx_oauth2_session.get(
        INSTRUCTOR_TASKS_URI,
        params=payload
    )
    return response.json()
