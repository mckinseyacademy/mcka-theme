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
from courses.controller import round_to_int, Proficiency, get_social_metrics, average_progress
from admin.models import Client

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

    data = {
        "name": course.name,
        "url": "https://www.mckinseyacademy.com{}".format(course.nav_url),
        "overview": overview.about,
        "start_date": course.start.isoformat(),
        "end_date": course.end.isoformat(),
        "week": course.week,
        "status": course.status,
    }
    return data

@api_authenticate_protect
@api_user_protect
@api_json_response
def user_course(request):
    course = standard_data(request).get("course", None)
    overview = course_api.get_course_overview(course.id)
    proficiency = course_api.get_course_metrics_grades(course.id, user_id=request.user.id, grade_object_type=Proficiency)
    social = get_social_metrics(course.id, request.user.id)

    data = {
        "name": course.name,
        "url": "https://www.mckinseyacademy.com{}".format(course.nav_url),
        "overview": overview.about,
        "start_date": course.start.isoformat(),
        "end_date": course.end.isoformat(),
        "week": course.week,
        "status": course.status,
        "user": {
            "name": request.user.full_name,
            "email": request.user.email,
            "progress": {
                "value": course.user_progress,
                "cohort_avg": average_progress(course, request.user.id)
            },
            "proficiency": {
                "value": round_to_int(proficiency.user_grade_value * 100),
                "cohort_avg": proficiency.course_average_display,
            },
            "social": {
                "value": social['points'],
                "cohort_avg": social['course_avg'],
            }
        }
    }
    return data

@api_authenticate_protect
@api_json_response
def users(request):
    client = Client.fetch(request.organization.client_id)
    students = client.fetch_students_by_enrolled()
    data = {
        "name": client.display_name,
        "contact_email": client.contact_email,
        "students": [],
    }

    for student in students:
        data["students"].append({
            "name": student.full_name,
            "email": student.email,
            "city": student.city,
            "country": student.country,
            "course_count": student.course_count,
        })

    return data
