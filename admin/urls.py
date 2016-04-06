from django.conf.urls import patterns, url
from admin import views

urlpatterns = patterns(
    'admin',
    url(r'^$', views.home, name='admin_home'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/(?P<user_id>[0-9]+)/unenroll$', views.client_admin_unenroll_participant, name='client_admin_unenroll'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/(?P<user_id>[0-9]+)/edit-email$', views.client_admin_edit_email, name='client_admin_edit_email'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/email_not_started$', views.client_admin_email_not_started, name='client_admin_email_not_started'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/download_course_report$', views.client_admin_download_course_report, name='download_course_report'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants$', views.client_admin_course_participants, name='client_admin_course_participants'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding/edit$', views.client_admin_branding_settings_edit, name='client_admin_branding_settings_edit'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding/reset$', views.client_admin_branding_settings_reset, name='client_admin_branding_settings_reset'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding$', views.client_admin_branding_settings, name='client_admin_branding_settings'),
    #LD DiscoverContent
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard/discover/list$', views.client_admin_course_learner_dashboard_discover_list, name='client_admin_course_learner_dashboard_discover_list'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard/discover/create$', views.client_admin_course_learner_dashboard_discover_create_edit, name='client_admin_course_learner_dashboard_discover_create_edit'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard/discover/edit/(?P<discovery_id>.*)$', views.client_admin_course_learner_dashboard_discover_create_edit, name='client_admin_course_learner_dashboard_discover_create_edit'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard/discover/delete/(?P<discovery_id>.*)$', views.client_admin_course_learner_dashboard_discover_delete, name='client_admin_course_learner_dashboard_discover_delete'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard/discover/list/reorder$', views.client_admin_course_learner_dashboard_discover_reorder, name='client_admin_course_learner_dashboard_discover_reorder'),
    #LD DiscoverContent
    #Learner Dashboard, Tile 
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/tile/(?P<tile_id>.*)$', views.client_admin_course_learner_dashboard_tile, name='client_admin_course_learner_dashboard_tile'),    
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/learner_dashboard$', views.client_admin_course_learner_dashboard, name='client_admin_course_learner_dashboard'),
    #Learner Dashboard, Tile 
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/analytics/participant$', views.client_admin_course_analytics_participants, name='client_admin_course_analytics_participants'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/analytics/progress$', views.client_admin_course_analytics_progress, name='client_admin_course_analytics_progress'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/analytics$', views.client_admin_course_analytics, name='client_admin_course_analytics'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/status$', views.client_admin_course_status, name='client_admin_course_status'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/users/(?P<user_id>[0-9]+)/progress$', views.client_admin_user_progress, name='client_admin_user_progress'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)$', views.client_admin_course, name='client_admin_course'),
    url(r'^client-admin/programs/(?P<program_id>.+)/download_program_report', views.client_admin_download_program_report, name='download_program_report'),
    url(r'^client-admin/programs', views.client_admin_program_detail, name='client_admin_program_detail'),
    url(r'^client-admin/contact', views.client_admin_contact, name='client_admin_contact'),
    url(r'^client-admin/(?P<client_id>[0-9]*)', views.client_admin_home, name='client_admin_home'),
    
    url(r'^api/courses/(?P<course_id>.*)/stats/$', views.course_details_stats_api.as_view(), name='course_details_stats_api'),
    url(r'^api/courses/(?P<course_id>.*)/engagement/$', views.course_details_engagement_api.as_view(), name='course_details_engagement_api'),
    url(r'^api/courses/(?P<course_id>.*)/performance/$', views.course_details_performance_api.as_view(), name='course_details_performance_api'),
    url(r'^api/courses/(?P<course_id>.*)/timeline/$', views.course_details_cohort_timeline_api.as_view(), name='course_details_cohort_timeline_api'),
    url(r'^api/courses/(?P<course_id>.+)$', views.course_details_api.as_view(), name='course_details_api'),
    url(r'^api/courses$', views.courses_list_api.as_view(), name='courses_list_api'),
    url(r'^courses/(?P<course_id>.*)/download_course_stats/$', views.download_course_stats, name='download_course_stats'),
    url(r'^courses/(?P<course_id>.*)/$', views.course_details, name='course_details'),
    url(r'^courses/$', views.courses_list, name='courses_list'),

    url(r'^course-meta-content$', views.course_meta_content_course_list, name='course_meta_content_course_list'),
    url(r'^course-meta-content/items/(?P<course_id>.+)$', views.course_meta_content_course_items, name='course_meta_content_course_items'),
    url(r'^course-meta-content/item/new', views.course_meta_content_course_item_new, name='course_meta_content_course_item_new'),
    url(r'^course-meta-content/item/(?P<item_id>[0-9]+)/edit', views.course_meta_content_course_item_edit, name='course_meta_content_course_item_edit'),
    url(r'^course-meta-content/item/(?P<item_id>[0-9]+)/delete', views.course_meta_content_course_item_delete, name='course_meta_content_course_item_delete'),

    url(r'^not_authorized', views.not_authorized, name='not_authorized'),

    url(r'^clients/client_new', views.client_new, name='client_new'),
    url(r'^clients/(?P<client_id>[0-9]+)/edit', views.client_edit, name='client_edit'),
    url(r'^clients/(?P<client_id>[0-9]+)$', views.client_detail, name='client_detail'),
    url(r'^clients/(?P<client_id>[0-9]+)/upload_student_list/check/(?P<task_key>.*)$', views.upload_student_list_check, name='upload_student_list_check'),
    url(r'^clients/(?P<client_id>[0-9]+)/upload_student_list', views.upload_student_list, name='upload_student_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/mass_student_enroll/check/(?P<task_key>.*)$', views.mass_student_enroll_check, name='mass_student_enroll_check'),
    url(r'^clients/(?P<client_id>[0-9]+)/mass_student_enroll', views.mass_student_enroll, name='mass_student_enroll'),
    url(r'^clients/(?P<client_id>[0-9]+)/change_company_image', views.change_company_image, name='change_company_image'),
    url(r'^clients/(?P<client_id>[0-9]+)/upload_company_image', views.upload_company_image, name='upload_company_image'),
    url(r'^clients/(?P<client_id>[0-9]+)/image/edit$', views.company_image_edit, name='company_image_edit'),
    url(r'^clients/new/change_company_image', views.change_company_image, name='change_company_image'),
    url(r'^clients/new/upload_company_image', views.upload_company_image, name='upload_company_image'),
    url(r'^clients/new/image/edit$', views.company_image_edit, name='company_image_edit'),
    url(r'^clients/(?P<client_id>[0-9]+)/download_student_list', views.download_student_list, name='download_student_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/program_association', views.program_association, name='program_association'),
    url(r'^clients/(?P<client_id>[0-9]+)/add_students_to_program', views.add_students_to_program, name='add_students_to_program'),
    url(r'^clients/(?P<client_id>[0-9]+)/add_students_to_course', views.add_students_to_course, name='add_students_to_course'),
    url(r'^clients/(?P<client_id>[0-9]+)/user/(?P<user_id>[0-9]+)/resend', views.client_resend_user_invite, name='client_resend_user_invite'),
    url(r'^clients/(?P<client_id>[0-9]+)/contact/add', views.client_detail_add_contact, name='client_detail_add_contact'),
    url(r'^clients/(?P<client_id>[0-9]+)/contact/(?P<user_id>[0-9]+)/remove', views.client_detail_remove_contact, name='client_detail_remove_contact'),
    url(r'^clients/(?P<client_id>[0-9]+)/contact', views.client_detail_contact, name='client_detail_contact'),
    url(r'^clients/(?P<client_id>[0-9]+)/navigation', views.client_detail_navigation, name='client_detail_navigation'),
    url(r'^clients/(?P<client_id>[0-9]+)/nav_links', views.client_detail_nav_links, name='client_detail_nav_links'),
    url(r'^clients/(?P<client_id>[0-9]+)/customization', views.client_detail_customization, name='client_detail_customization'),
    url(r'^clients/(?P<client_id>[0-9]+)/access_keys/create', views.create_access_key, name='create_access_key'),
    url(r'^clients/(?P<client_id>[0-9]+)/access_keys/(?P<access_key_id>[0-9]+)/share', views.share_access_key, name='share_access_key'),
    url(r'^clients/(?P<client_id>[0-9]+)/access_keys', views.access_key_list, name='access_key_list'),
    url(r'^clients/(?P<client_id>[0-9]+)/(?P<detail_view>.*)', views.client_detail, name='client_detail'),
    url(r'^clients', views.client_list, name='client_list'),

    url(r'^programs/program_new', views.program_new, name='program_new'),
    url(r'^programs/(?P<program_id>[0-9]+)/edit', views.program_edit, name='program_edit'),
    url(r'^programs/(?P<program_id>[0-9]+)$', views.program_detail, name='program_detail'),
    url(r'^programs/(?P<program_id>[0-9]+)/add_courses', views.add_courses, name='add_courses'),
    url(r'^programs/(?P<program_id>[0-9]+)/download_program_report', views.download_program_report, name='download_program_report'),
    url(r'^programs/(?P<program_id>[0-9]+)/(?P<detail_view>.*)', views.program_detail, name='program_detail'),
    url(r'^programs', views.program_list, name='program_list'),

    url(r'^workgroup/dashboard$', views.groupwork_dashboard, name='groupwork_dashboard'),
    url(r'^workgroup/dashboard/my_links/(?:(?P<link_id>\d+)/)?$', views.QuickLinkView.as_view(),
        name='groupwork_dashboard_links'),
    url(r'^workgroup/dashboard/programs/(?P<program_id>.*)/courses$', views.groupwork_dashboard_courses, name='groupwork_dashboard_courses'),
    url(r'^workgroup/dashboard/companies$', views.groupwork_dashboard_companies, name='groupwork_dashboard_companies'),
    url(r'^workgroup/dashboard/courses/(?P<course_id>.*)/projects$', views.groupwork_dashboard_projects, name='groupwork_dashboard_projects'),
    url(r'^workgroup/dashboard/programs/(?P<program_id>.*)/courses/(?P<course_id>.*)/projects/(?P<project_id>.*)/details$', views.groupwork_dashboard_details, name='groupwork_dashboard_details'),
    url(r'^workgroup/course/(?P<course_id>.*)/download_group_list', views.download_group_list, name='download_group_list'),
    url(r'^workgroup/course/(?P<course_id>.*)/download_group_projects_report', views.download_group_projects_report, name='download_group_projects_report'),
    url(r'^workgroup/course/(?P<course_id>.*)/group_work_status/(?P<group_id>.*)', views.group_work_status, name='group_work_status'),
    url(r'^workgroup/course/(?P<course_id>.*)/group_work_status', views.group_work_status, name='group_work_status'),
    url(r'^workgroup/course/(?P<course_id>.*)/detail/(?P<workgroup_id>.*)', views.workgroup_detail, name='workgroup_detail'),
    url(r'^workgroup/course/(?P<course_id>.*)/assignments', views.workgroup_course_assignments, name='workgroup_course_assignments'),
    url(r'^workgroup/course/(?P<course_id>.*)', views.workgroup_course_detail, name='workgroup_course_detail'),
    url(r'^workgroup/programs/list', views.workgroup_programs_list, name='workgroup_programs_list'),
    url(r'^workgroup/group/update/(?P<group_id>[0-9]+)/(?P<course_id>.*)', views.workgroup_group_update, name='workgroup_group_update'),
    url(r'^workgroup/group/create/(?P<course_id>.*)', views.workgroup_group_create, name='workgroup_group_create'),
    url(r'^workgroup/group/(?P<group_id>[0-9]+)/remove', views.workgroup_group_remove, name='workgroup_group_remove'),
    url(r'^workgroup/project/create/(?P<course_id>.*)', views.workgroup_project_create, name='workgroup_project_create'),
    url(r'^workgroup/project/(?P<project_id>[0-9]+)/delete', views.workgroup_remove_project, name='workgroup_remove_project'),
    url(r'^workgroup', views.workgroup_list, name='workgroup_list'),

    url(r'^api/participants/(?P<user_id>[0-9]+)/active_courses$', views.participant_details_active_courses_api.as_view(), name='participant_details_active_courses_api'),
    url(r'^api/participants/(?P<user_id>[0-9]+)/course_history$', views.participant_details_course_history_api.as_view(), name='participant_details_course_history_api'),
    url(r'^api/participants$', views.participants_list_api.as_view(), name='participants_list_api'),
    url(r'^participants/(?P<user_id>[0-9]+)', views.participant_details_api.as_view(), name='participants_details'),
    url(r'^participants$', views.participants_list, name='participants_list'),

    url(r'^permissions/(?P<user_id>[0-9]+)/edit', views.edit_permissions, name='edit_permissions'),
    url(r'^permissions', views.permissions, name='permissions'),

    url(r'^project/(?P<project_id>.*)/activity/(?P<activity_id>.*)/generate_assignments', views.generate_assignments, name='generate_assignments')
)
