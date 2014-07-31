from django.conf.urls import patterns, url
from admin import views

urlpatterns = patterns(
    'admin',
    url(r'^$', views.home, name='admin_home'),
    url(r'^client-admin$', views.client_admin_home, name='client_admin_home'),
    url(r'^course-meta-content$', views.course_meta_content_course_list, name='course_meta_content_course_list'),
    url(r'^course-meta-content/items', views.course_meta_content_course_items, name='course_meta_content_course_items'),
    url(r'^course-meta-content/item/new', views.course_meta_content_course_item_new, name='course_meta_content_course_item_new'),
    url(r'^course-meta-content/item/(?P<item_id>[0-9]+)/edit', views.course_meta_content_course_item_edit, name='course_meta_content_course_item_edit'),
    url(r'^course-meta-content/item/(?P<item_id>[0-9]+)/delete', views.course_meta_content_course_item_delete, name='course_meta_content_course_item_delete'),
    url(r'^not_authorized', views.not_authorized, name='not_authorized'),
    url(r'^clients/client_new', views.client_new, name='client_new'),
    url(r'^clients/(?P<client_id>[0-9]+)/edit', views.client_edit, name='client_edit'),
    url(r'^clients/(?P<client_id>[0-9]+)$', views.client_detail, name='client_detail'),
    url(r'^clients/(?P<client_id>[0-9]+)/upload_student_list', views.upload_student_list, name='upload_student_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/download_student_list', views.download_student_list, name='download_student_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/program_association', views.program_association, name='program_association'),
    url(r'^clients/(?P<client_id>[0-9]+)/add_students_to_program', views.add_students_to_program, name='add_students_to_program'),
    url(r'^clients/(?P<client_id>[0-9]+)/add_students_to_course', views.add_students_to_course, name='add_students_to_course'),
    url(r'^clients/(?P<client_id>[0-9]+)/user/(?P<user_id>[0-9]+)/resend', views.client_resend_user_invite, name='client_resend_user_invite'),
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
    url(r'^workgroup/course/(?P<course_id>.*)/download_group_projects_report', views.download_group_projects_report, name='download_group_projects_report'),
    url(r'^workgroup/course/(?P<course_id>.*)/generate_assignments', views.generate_assignments, name='generate_assignments'),
    url(r'^workgroup/course/(?P<course_id>.*)/detail/(?P<workgroup_id>.*)', views.workgroup_detail, name='workgroup_detail'),
    url(r'^workgroup/course/(?P<course_id>.*)', views.workgroup_course_detail, name='workgroup_course_detail'),
    url(r'^workgroup/programs/list', views.workgroup_programs_list, name='workgroup_programs_list'),
    url(r'^workgroup/group/update/(?P<group_id>[0-9]+)/(?P<course_id>.*)', views.workgroup_group_update, name='workgroup_group_update'),
    url(r'^workgroup/group/create/(?P<course_id>.*)', views.workgroup_group_create, name='workgroup_group_create'),
    url(r'^workgroup/group/(?P<group_id>[0-9]+)/remove', views.workgroup_group_remove, name='workgroup_group_remove'),
    url(r'^workgroup/project/create/(?P<course_id>.*)', views.workgroup_project_create, name='workgroup_project_create'),
    url(r'^workgroup', views.workgroup_list, name='workgroup_list'),
    url(r'^permissions/(?P<user_id>[0-9]+)/edit', views.edit_permissions, name='edit_permissions'),
    url(r'^permissions', views.permissions, name='permissions'),
)
