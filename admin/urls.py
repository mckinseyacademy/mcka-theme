from django.conf.urls import patterns, url
from admin import views

urlpatterns = patterns(
    'admin',
    url(r'^$', views.home, name='admin_home'),
    url(r'^course_meta_content', views.course_meta_content, name='course_meta_content'),
    url(r'^not_authorized', views.not_authorized, name='not_authorized'),
    url(r'^clients/client_new', views.client_new, name='client_new'),
    url(r'^clients/(?P<client_id>[0-9]+)/edit', views.client_edit, name='client_edit'),
    url(r'^clients/(?P<client_id>[0-9]+)$', views.client_detail, name='client_detail'),
    url(r'^clients/(?P<client_id>[0-9]+)/upload_student_list', views.upload_student_list, name='upload_student_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/download_student_list', views.download_student_list, name='download_student_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/program_association', views.program_association, name='program_association'),
    url(r'^clients/(?P<client_id>[0-9]+)/add_students_to_program', views.add_students_to_program, name='add_students_to_program'),
    url(r'^clients/(?P<client_id>[0-9]+)/add_students_to_course', views.add_students_to_course, name='add_students_to_course'),
    url(r'^clients/(?P<client_id>[0-9]+)/(?P<detail_view>.*)', views.client_detail, name='client_detail'),
    url(r'^clients', views.client_list, name='client_list'),
    url(r'^programs/program_new', views.program_new, name='program_new'),
    url(r'^programs/(?P<program_id>[0-9]+)/edit', views.program_edit, name='program_edit'),
    url(r'^programs/(?P<program_id>[0-9]+)$', views.program_detail, name='program_detail'),
    url(r'^programs/(?P<program_id>[0-9]+)/add_courses', views.add_courses, name='add_courses'),
    url(r'^programs/(?P<program_id>[0-9]+)/download_program_report', views.download_program_report, name='download_program_report'),
    url(r'^programs/(?P<program_id>[0-9]+)/(?P<detail_view>.*)', views.program_detail, name='program_detail'),
    url(r'^programs', views.program_list, name='program_list'),
    url(r'^workgroup/course/(?P<course_id>.*)/download_group_list', views.download_group_list, name='download_group_list'),
    url(r'^workgroup/course/(?P<course_id>.*)', views.workgroup_course_detail, name='workgroup_course_detail'),
    url(r'^workgroup/programs/list', views.workgroup_programs_list, name='workgroup_programs_list'),
    url(r'^workgroup/group/create/(?P<course_id>.*)', views.workgroup_group_create, name='workgroup_group_create'),
    url(r'^workgroup/group/(?P<group_id>[0-9]+)/remove', views.workgroup_group_remove, name='workgroup_group_remove'),
    url(r'^workgroup', views.workgroup_list, name='workgroup_list'),
)
