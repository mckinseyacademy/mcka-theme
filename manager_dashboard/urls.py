from django.urls import path, re_path

from . import views

urlpatterns = [

    re_path(
        r'^courses/(?P<course_id>.*)/average_scores$',
        views.get_average_progress_proficiency_course,
        name='manager_course_average_progress_proficiency'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)$',
        views.ManagerReportsCourseDetailsApi.as_view(),
        name='manager_reports_course_details_api'
    ),
    path('team_report', views.manager_team_reports, name='manager_dashboard'),
    re_path(
        r'^student_report/(?P<username>.+)/course/(?P<course_id>.+)/$',
        views.StudentCourseProgressDetailsApi.as_view(),
        name='manager_reports_student_course_progress_details_api'
    ),
]
