''' json for public api requests '''
import json
import datetime
import functools

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from api_client import course_api, user_api, workgroup_api
from api_protect import api_json_response, api_authenticate_protect, api_user_protect
from .models import ApiToken
from lib.authorization import permission_group_required
from api_client.group_api import PERMISSION_GROUPS
from courses.user_courses import standard_data

@require_POST
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
@api_json_response
def api_create_token(request):
    api_token = ApiToken(
        client_id = request.POST['client_id']
    )
    api_token.save()
    return api_token.as_json()

@api_authenticate_protect
@api_json_response
def course(request, course_id):
    course = course_api.get_course(course_id)
    overview = course_api.get_course_overview(course_id)
    status = None
    week = None

    if course.ended:
        status = "COURSE_ENDED"
    elif course.started:
        status = "COURSE_STARTED"
        week = course.week
    else:
        status = "COURSE_UNAVAILABLE"

    data = {
        "name": course.name,
        "url": "https://www.mckinseyacademy.com/courses/{}".format(course_id),
        "overview": overview.about,
        "start_date": course.start.isoformat(),
        "end_date": course.end.isoformat(),
        "week": week,
        "status": status,
    }
    return data

@api_authenticate_protect
@api_user_protect
@api_json_response
def user_course(request):
    course = standard_data(request).get("course", None)
    overview = course_api.get_course_overview(course.id)
    status = None
    week = None

    data = {
        "name": course.name,
        "url": "https://www.mckinseyacademy.com/courses/{}".format(course.id),
        "overview": overview.about,
        "start_date": course.start.isoformat(),
        "end_date": course.end.isoformat(),
        "week": week,
        "status": status,
    }
    return data
