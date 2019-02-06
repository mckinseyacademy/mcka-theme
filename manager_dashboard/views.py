import json

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from admin.controller import CourseParticipantStats, load_course
from api_client import user_api, course_api
from api_client.course_api import get_course_enrollments, get_course_list, get_course_completions, \
    get_course_cohort_settings
from api_client.group_api import PERMISSION_GROUPS
from api_data_manager.course_data import CourseDataManager, COURSE_PROPERTIES
from courses.controller import Proficiency, Progress
from lib.authorization import permission_group_required
from api_client.oauth2_requests import get_oauth2_session
from controller import get_user_progress


@permission_group_required(PERMISSION_GROUPS.MANAGER)
def manager_team_reports(request):
    direct_reports = ManagerReportsCourseDetailsApi().get(request=request)
    reports_username = [report.username for report in direct_reports]
    enrollments = get_course_enrollments(usernames=reports_username)
    course_ids = list(set([enrollment.course_id for enrollment in enrollments if enrollment.is_active]))
    manager_courses = get_course_list(course_ids) if course_ids else []
    manager_courses_list = []
    for index, course in enumerate(manager_courses):
        cohorts_enabled = get_course_cohort_settings(course.id).is_cohorted
        manager_courses_list.append((index, course.id, course.name, cohorts_enabled))
    return render(request, 'admin/manager_dashboard/team_report.haml', {'manager_courses': manager_courses_list})


class ManagerReportsCourseDetailsApi(APIView):
    """
    Fetch the course participant stats for the current user's direct reports.

    Any logged-in user can invoke this API, but only those with direct reports will see any data.
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id=None, *args, **kwargs):
        """
        Perform the request, assuming the current user is the manager fetching the report.
        """
        direct_reports = user_api.get_reports_for_manager(request.user.email)
        request_params = request.GET.copy()
        if course_id:
            course_participants_stats = CourseParticipantStats(
                course_id=course_id,
                restrict_to_participants=direct_reports,
                base_url=request.build_absolute_uri())
            course_participants = course_participants_stats.get_participants_data(request_params)
            return Response(course_participants)
        else:
            return direct_reports


class StudentCourseProgressDetailsApi(APIView):
    """
    Fetch the student lesson by lesson progress for the current course
    Like Lesson 1: ABC    100% Completed

    Any logged-in user can invoke this API, but only those with direct reports will see any data.
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, username=None, course_id=None):
        """
        Perform the request, assuming the current user is the manager fetching the report.
        """
        # check if the logged in user is the manager of the given student
        # if so, proceed with the data
        edx_oauth2_session = get_oauth2_session()
        user_progress = get_course_completions(course_id, username,
                                               extra_fields='chapter',
                                               edx_oauth2_session=edx_oauth2_session,
                                               )
        user_course_progress = []
        course_details = load_course(course_id, request=request, depth=5)
        user_chapters = []
        if user_progress:
            user_chapters = user_progress.get(username)
        if course_details and user_chapters:
            user_course_progress = get_user_progress(course_details, user_chapters)
        return Response(user_course_progress)


@permission_group_required(PERMISSION_GROUPS.MANAGER)
def get_average_progress_proficiency_course(request, course_id):
    """ Get course's overall proficiency and progress for manager dashboard"""

    avg_course_scores = CourseDataManager(course_id).get_cached_data(property_name=COURSE_PROPERTIES.AVERAGE_SCORES)

    if avg_course_scores is None:
        proficiency = course_api.get_course_metrics_grades(
            course_id,
            user_id=request.user.id,
            skipleaders=True,
            grade_object_type=Proficiency
        )

        progress = course_api.get_course_metrics_completions(
            course_id,
            user_id=request.user.id,
            skipleaders=True,
            completions_object_type=Progress
        )
        avg_course_scores = {
            'avg_progress': progress.course_average_display,
            'avg_proficiency': proficiency.course_average_display
        }
        CourseDataManager(course_id).set_cached_data(
            property_name=COURSE_PROPERTIES.AVERAGE_SCORES, data=avg_course_scores
        )

    return HttpResponse(json.dumps(avg_course_scores), content_type='application/json')