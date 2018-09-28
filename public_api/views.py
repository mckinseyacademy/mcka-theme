''' json for public api requests '''
import re
import json
import datetime
import functools

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _
from api_client import course_api, user_api, workgroup_api
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from accounts.controller import send_password_reset_email
from api_client import course_api, user_api
from api_protect import api_json_response, api_authenticate_protect, api_user_protect
from mcka_apros import settings
from .models import ApiToken
from lib.authorization import permission_group_required
from api_client.group_api import PERMISSION_GROUPS
from courses.user_courses import standard_data
from courses.controller import round_to_int, Proficiency, get_user_social_metrics, average_progress, load_static_tabs
from admin.models import Client
from .serializers import ResetPasswordSerializer
from public_api.controller import get_course_ff_and_custom_taxonomy, \
    create_and_add_course_ff_and_custom_taxonomy_in_list


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
    proficiency = course_api.get_course_metrics_grades(
        course.id, user_id=request.user.id, skipleaders=True, grade_object_type=Proficiency
    )
    social = get_user_social_metrics(request.user.id, course.id)
    article = load_static_tabs(course.id, "article")

    data = {
        "name": course.name,
        "url": "https://www.mckinseyacademy.com{}".format(course.nav_url),
        "overview": overview.about,
        "start_date": course.start.isoformat(),
        "end_date": course.end.isoformat() if course.end else None,
        "week": course.week,
        "status": course.status,
        "user": {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": request.user.username,
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

    if article:
        try:
            data["article"] = {
                "title": re.search(r'data-title="([^"]+)"', article.content).group(1),
                "author": re.search(r'data-author="([^"]+)"', article.content).group(1),
                "url": "https://www.mckinseyacademy.com{}/article".format(course.nav_url),
                "excerpt": re.search(r'data-excerpt="([^"]+)"', article.content).group(1),
            }
        except:
            data["article"] = None

    return data


@api_authenticate_protect
@api_json_response
def users(request):
    client = Client.fetch(request.organization.client_id)
    students = client.fetch_students_by_enrolled()
    return {"error": _("Student information not found")}

    data = {
        "name": client.display_name,
        "contact_email": client.contact_email,
        "students": [],
    }

    for student in students:
        data["students"].append({
            "first_name": student.first_name,
            "last_name": student.last_name,
            "username": student.username,
            "email": student.email,
            "course_count": student.course_count,
        })

    return data


@api_view(['POST'])
def reset_password(request):
    """
    Send reset password email instructions
    """
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        users = user_api.get_users(email=serializer.validated_data['email'])
        if len(users) < 1:
            return Response({'errors': _('No such email exist')}, status=422)
        send_password_reset_email(
            request.META.get('HTTP_HOST'),
            users[0],
            request.is_secure(),
            subject_template_name='registration/password_reset_subject.txt',
            email_template_name='registration/password_reset_email.haml',
            from_email=settings.APROS_EMAIL_SENDER
        )

        return Response({'detail': _('Password reset email sent')}, status=status.HTTP_200_OK)
    else:
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


def get_course_feature_flag_and_custom_taxonomy(request, course_id=None):
    """ This api will return the feature flags and custom taxonomy for one course
     or all user courses depends on demand
    """
    course_ff_custom_taxonomy = []

    response, status_code = user_api.get_user_by_bearer_token()
    if not status_code == status.HTTP_200_OK:
        return HttpResponse(status=status_code)
    user_id = response['id']

    if course_id:
        course_feature_flag = get_course_ff_and_custom_taxonomy(user_id, course_ff_custom_taxonomy, course_id)
        if not course_feature_flag:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    else:
        courses = user_api.get_user_courses(user_id)
        for course in courses:
            create_and_add_course_ff_and_custom_taxonomy_in_list(course_ff_custom_taxonomy, course.id)

    return HttpResponse(
        json.dumps(course_ff_custom_taxonomy),
        content_type='application/json'
    )

