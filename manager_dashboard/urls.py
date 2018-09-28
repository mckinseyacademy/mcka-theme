from django.conf.urls import url

import views

urlpatterns = [
    url(r'^courses/(?P<course_id>.+)$', views.ManagerReportsCourseDetailsApi.as_view(), name='manager_reports_course_details_api'),
    url(r'^team_report', views.manager_team_reports, name='manager_dashboard'),
]
