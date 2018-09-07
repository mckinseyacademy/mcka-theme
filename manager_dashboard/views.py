from django.shortcuts import render
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from admin.controller import CourseParticipantStats
from api_client import user_api
from api_client.course_api import get_course_enrollments, get_course_list
from api_client.group_api import PERMISSION_GROUPS
from lib.authorization import permission_group_required


@permission_group_required(PERMISSION_GROUPS.MANAGER)
def manager_team_reports(request):
    direct_reports = ManagerReportsCourseDetailsApi().get(request=request)
    reports_username = [report.username for report in direct_reports]
    enrollments = get_course_enrollments(usernames=reports_username)
    course_ids = list(set([enrollment.course_id for enrollment in enrollments]))
    manager_courses = get_course_list(course_ids)
    manager_courses_list = []
    for index, course in enumerate(manager_courses):
        manager_courses_list.append((index, course.id, course.name))
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
        import pdb
        direct_reports = user_api.get_reports_for_manager(request.user.email)
        if course_id:
            course_participants_stats = CourseParticipantStats(
                course_id=course_id,
                restrict_to_participants=direct_reports,
                base_url=request.build_absolute_uri())
            course_participants = course_participants_stats.get_participants_data(request.GET)
            return Response(course_participants)
        else:
            return direct_reports
