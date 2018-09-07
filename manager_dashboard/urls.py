from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
	'',
	url(r'^courses/(?P<course_id>.+)$', views.ManagerReportsCourseDetailsApi.as_view(), name='manager_reports_course_details_api'),
	url(r'^team_report', views.manager_team_reports, name='manager_dashboard'),
)
