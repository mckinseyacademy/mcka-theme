''' json for public api requests '''
import re
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from accounts.views import get_user_from_login_id
from accounts.controller import send_password_reset_email
from accounts.models import UserActivation
from api_client import course_api, user_api
from .api_protect import api_json_response, api_authenticate_protect, api_user_protect
from mcka_apros import settings
from .models import ApiToken
from lib.authorization import permission_group_required
from api_client.group_api import PERMISSION_GROUPS
from courses.user_courses import standard_data
from courses.controller import round_to_int, Proficiency, get_user_social_metrics, average_progress, load_static_tabs
from admin.models import Client
from .serializers import ResetPasswordSerializer
from public_api.controller import get_course_ff_and_custom_taxonomy, \
    create_and_add_course_ff_and_custom_taxonomy_in_list, get_course_ff, \
    create_and_add_course_ff_in_list
from lib.mail import email_user_activation_link


@require_POST
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
@api_json_response
def api_create_token(request):
    api_token = ApiToken(client_id=request.POST['client_id'])
    api_token.save()
    return api_token.as_json()


@api_authenticate_protect
@api_json_response
def course(request, course_id):
    course_ = course_api.get_course_v1(course_id, depth=0)
    overview = course_api.get_course_overview(course_id)

    data = {
        "name": course_.name,
        "url": "https://www.mckinseyacademy.com{}".format(course_.nav_url),
        "overview": overview.about,
        "week": course_.week,
        "status": course_.status,
    }

    if course_.start:
        data["start_date"] = course_.start.isoformat()

    if course_.end:
        data["end_date"] = course_.end.isoformat()

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
        except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
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
            subject_template_name='registration/password_reset_subject.haml',
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


def get_course_feature_flag(request, course_id=None):
    """ This will return the feature flags for one course or all user courses depends on demand
    """
    feature_flag = []

    response, status_code = user_api.get_user_by_bearer_token()
    if not status_code == status.HTTP_200_OK:
        return HttpResponse(status=status_code)
    user_id = response['id']

    if course_id:
        course_feature_flag = get_course_ff(user_id, feature_flag, course_id)
        if not course_feature_flag:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    else:
        courses = user_api.get_user_courses(user_id)
        for course in courses:
            create_and_add_course_ff_in_list(feature_flag, course.id)

    return HttpResponse(
        json.dumps(feature_flag),
        content_type='application/json')


def send_participant_activation_link(request, login_id):

    user = get_user_from_login_id(login_id)
    if user:
        try:
            if not user.is_active:
                activation_record = UserActivation.get_user_activation(user)
                email_head = request.build_absolute_uri('/accounts/activate')
                activation_link = '{}/{}'.format(email_head, activation_record.activation_key)

                email_user_activation_link(request, user, activation_link)

                return JsonResponse({'message':
                                    _('We have sent an email to <a href="mailto:{0}">{0}</a>'
                                      ' with a link to create an account for you.')
                                    .format(user.get("email")), 'email': user.get("email")}, status=status.HTTP_200_OK)
        except Exception:  # pylint: disable=bare-except TODO: add specific Exception class:
            return JsonResponse({'error': _("Sorry, Please try again later to receive an email with a "
                                            "link to create your account.")}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': _('User does not exist')}, status=status.HTTP_400_BAD_REQUEST)
