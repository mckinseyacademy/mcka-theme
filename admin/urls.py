from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from admin import views
from admin import cache as cache_views
from admin import s3 as s3views
from certificates import views as certificate_views

router = SimpleRouter()
router.register(r'^api/mobileapps', views.MobileAppsApi, base_name='mobileapps_api')

urlpatterns = router.urls
urlpatterns += [
    url(r'^$', views.home, name='admin_home'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/(?P<user_id>[0-9]+)/unenroll$', views.client_admin_unenroll_participant, name='client_admin_unenroll'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/(?P<user_id>[0-9]+)/edit-email$', views.client_admin_edit_email, name='client_admin_edit_email'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/email_not_started$', views.client_admin_email_not_started, name='client_admin_email_not_started'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/download_course_report$', views.client_admin_download_course_report, name='download_course_report'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants$', views.client_admin_course_participants, name='client_admin_course_participants'),

    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding/reset$', views.client_admin_branding_settings_reset, name='client_admin_branding_settings_reset'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding$', views.client_admin_branding_settings, name='client_admin_branding_settings'),
    url(r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding/create_edit$', views.client_admin_branding_settings_create_edit, name='client_admin_branding_settings_create_edit'),

    #Learner dashboard urls
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/branding_reset$', views.course_learner_dashboard_branding_reset, name='course_learner_dashboard_branding_reset'),
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/branding$', views.course_learner_dashboard_branding, name='course_learner_dashboard_branding'),

    url(r'^courses/(?P<course_id>.+)/learner_dashboard/discover/list$', views.course_learner_dashboard_discover_list, name='course_learner_dashboard_discover_list'),
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/discover/create$', views.course_learner_dashboard_discover_create_edit, name='course_learner_dashboard_discover_create_edit'),
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/discover/edit/(?P<discovery_id>.*)$', views.course_learner_dashboard_discover_create_edit, name='course_learner_dashboard_discover_create_edit'),
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/discover/delete/(?P<discovery_id>.*)$', views.course_learner_dashboard_discover_create_edit, name='course_learner_dashboard_discover_create_edit'),
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/discover/list/reorder$', views.course_learner_dashboard_discover_reorder, name='course_learner_dashboard_discover_reorder'),

    url(r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/duplicate/(?P<copy_to_course_id>.+)$', views.course_learner_dashboard_copy, name='course_learner_dashboard_copy'),

    url(r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/tile/(?P<tile_id>.*)$', views.course_learner_dashboard_tile, name='course_learner_dashboard_tile'),
    url(r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/element_reorder$', views.course_learner_dashboard_tile_reorder, name='course_learner_dashboard_tile_reorder'),
    url(r'^courses/(?P<course_id>.*)/learner_dashboard', views.course_learner_dashboard, name='course_learner_dashboard'),
    #Learner dashboard urls

    #Demo registration CMS urls
    url(r'^course_runs/$', views.course_run_list, name='course_run_list'),
    url(r'^course_run/view/(?P<course_run_id>.+)/$', views.course_run_view, name='course_run_view'),
    url(r'^course_run/create/$', views.course_run_create_edit, name='course_run_create_edit'),
    url(r'^course_run/create/(?P<course_run_id>.+)$', views.course_run_create_edit, name='course_run_create_edit'),
    url(r'^course_run/csv_download/(?P<course_run_id>.+)/$', views.course_run_csv_download, name='course_run_csv_download'),
    url(r'^course_run/edit$', views.EditAndDeleteSelfRegRole.as_view(),
        name='edit_and_delete_self_reg_role'),

    #Demo registration CMS urls

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

    url(r'^api/courses/(?P<course_id>.*)/edit_course_meta_data/$', views.CourseMetaDataApiView.as_view(),
        name='course_meta_data_api_view'),
    url(r'^api/courses/(?P<course_id>.*)/stats/$', views.course_details_stats_api.as_view(), name='course_details_stats_api'),
    url(r'^api/courses/(?P<course_id>.*)/engagement/$', views.course_details_engagement_api.as_view(), name='course_details_engagement_api'),
    url(r'^api/courses/(?P<course_id>.*)/performance/$', views.course_details_performance_api.as_view(), name='course_details_performance_api'),
    url(r'^api/courses/(?P<course_id>.*)/timeline/$', views.course_details_cohort_timeline_api.as_view(), name='course_details_cohort_timeline_api'),
    url(r'^api/courses/(?P<course_id>.*)/tags$', views.course_details_tags_api.as_view(), name='course_details_tags_api'),
    url(r'^api/courses/(?P<course_id>.+)$', views.CourseDetailsApi.as_view(), name='course_details_api'),
    url(r'^api/courses$', views.courses_list_api.as_view(), name='courses_list_api'),
    url(r'^courses/(?P<course_id>.*)/download_course_stats/$', views.download_course_stats, name='download_course_stats'),
    url(
        r'^download_task_generated_csv/(?P<task_id>[-\w]+)/$',
        views.download_task_generated_csv, name='download_task_generated_csv'
    ),
    url(r'^courses/(?P<course_id>.*)/$', views.course_details, name='course_details'),
    url(r'^courses/$', views.courses_list, name='courses_list'),

    url(r'^course-meta-content$', views.course_meta_content_course_list, name='course_meta_content_course_list'),
    url(r'^course-meta-content/items/(?P<course_id>.+)$', views.course_meta_content_course_items, name='course_meta_content_course_items'),
    url(r'^course-meta-content/item/new', views.course_meta_content_course_item_new, name='course_meta_content_course_item_new'),
    url(r'^course-meta-content/item/(?P<item_id>[0-9]+)/edit', views.course_meta_content_course_item_edit, name='course_meta_content_course_item_edit'),
    url(r'^course-meta-content/item/(?P<item_id>[0-9]+)/delete', views.course_meta_content_course_item_delete, name='course_meta_content_course_item_delete'),

    url(r'^not_authorized', views.not_authorized, name='not_authorized'),

    url(r'^api/clients/(?P<client_id>[0-9]+)/download_student_list', views.download_student_list_api.as_view(), name='download_student_list_api'),
    url(r'^clients/client_new', views.client_new, name='client_new'),
    url(r'^clients/(?P<client_id>[0-9]+)/edit$', views.client_edit, name='client_edit'),
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
    url(r'^clients/(?P<client_id>[0-9]+)/(?P<img_type>[a-z]+)/edit_client_mobile_image$', views.edit_client_mobile_image, name='edit_client_mobile_image'),
    url(r'^clients/(?P<client_id>[0-9]+)/nav_links', views.client_detail_nav_links, name='client_detail_nav_links'),
    url(r'^clients/(?P<client_id>[0-9]+)/remove_image',
        views.remove_client_branding_image,
        name='remove_client_branding_image'),
    url(r'^clients/(?P<client_id>[0-9]+)/customization', views.client_detail_customization, name='client_detail_customization'),
    url(r'^clients/(?P<client_id>[0-9]+)/sso/create-access-key', views.create_access_key, name='create_access_key'),
    url(r'^clients/(?P<client_id>[0-9]+)/sso/course-create-api', views.create_course_access_key_api.as_view(), name='create_course_access_key_api'),
    url(r'^clients/(?P<client_id>[0-9]+)/sso/course-create', views.create_course_access_key, name='create_course_access_key'),
    url(r'^clients/(?P<client_id>[0-9]+)/sso/(?P<access_key_id>[0-9]+)/share', views.share_access_key, name='share_access_key'),
    url(r'^clients/(?P<client_id>[0-9]+)/sso', views.client_sso, name='client_sso'),
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
    url(r'^workgroup/dashboardV2/companies$', views.groupwork_dashboard_companiesV2, name='groupwork_dashboard_companies'),
    url(r'^workgroup/dashboardV2$', views.groupwork_dashboardV2, name='groupwork_dashboardV2'),
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

    url(r'^api/participants/(?P<user_id>[0-9]+)/active_courses/export_stats$', views.download_active_courses_stats, name='download_active_courses_stats'),
    url(r'^api/participants/(?P<user_id>[0-9]+)/course_history/export_stats$', views.download_course_history_stats, name='download_course_history_stats'),
    url(r'^api/participants/(?P<user_id>[0-9]+)/active_courses$', views.participant_details_active_courses_api.as_view(), name='participant_details_active_courses_api'),
    url(r'^api/participants/(?P<user_id>[0-9]+)/course_history$', views.participant_details_course_history_api.as_view(), name='participant_details_course_history_api'),
    url(r'^api/participants/(?P<user_id>[0-9]+)/course_manage/(?P<course_id>.+)$', views.participant_course_manage_api.as_view(), name='participant_course_manage_api'),
    url(r'^api/participants/(?P<user_id>[0-9]+)/admin_companies', views.users_company_admin_get_post_put_delete_api.as_view(), name='users_company_admin_get_post_put_delete_api'),
    url(r'^api/participants/organizations$', views.manage_user_company_api.as_view(), name='manage_user_company_api'),
    url(r'^api/participants/courses$', views.manage_user_courses_api.as_view(), name='manage_user_courses_api'),
    url(r'^api/participants/validate_participant_email/$', views.validate_participant_email, name='validate_participant_email'),
    url(r'^api/participants/validate_participant_username/$', views.validate_participant_username, name='validate_participant_username'),
    url(r'^api/participants/import_participants/check/(?P<task_key>.*)$', views.import_participants_check, name='import_participants_check'),
    url(r'^api/participants/import_participants/download_activation_links/$', views.download_activation_links_by_task_key, name='download_activation_links_by_task_key'),
    url(r'^api/participants/import_participants$', views.import_participants, name='import_participants'),
    url(r'^api/participants/enroll_participants_from_csv/check/(?P<task_key>.*)$', views.import_participants_check, name='import_participants_check'),
    url(r'^api/participants/enroll_participants_from_csv$', views.enroll_participants_from_csv, name='enroll_participants_from_csv'),
    url(r'^api/participants$', views.ParticipantsListApi.as_view(), name='participants_list_api'),
    url(r'^participants/(?P<user_id>[0-9]+)/courses/(?P<course_id>.*)/unenroll$', views.participant_details_courses_unenroll_api.as_view(), name='participant_details_courses_unenroll_api'),
    url(r'^participants/(?P<user_id>[0-9]+)/courses/(?P<course_id>.*)/edit_status$', views.participant_details_course_edit_status_api.as_view(), name='participant_details_course_edit_status_api'),
    url(r'^participants/(?P<user_id>[0-9]+)/resend_activation_link', views.participant_mail_activation_link, name='participant_mail_activation_link'),
    url(r'^participants/(?P<user_id>[0-9]+)/reset_password', views.participant_password_reset, name='participant_password_reset'),
    url(r'^participants/(?P<user_id>[0-9]+)', views.participant_details_api.as_view(), name='participants_details'),
    url(r'^participants$', views.participants_list, name='participants_list'),

    url(r'^api/companies/(?P<company_id>[0-9]+)/linkedapps$', views.CompanyLinkedAppsApi.as_view(), name='company_linked_apps_api'),
    url(r'^api/companies/(?P<company_id>[0-9]+)/courses$', views.CompanyCoursesApi.as_view(), name='company_courses_api'),
    url(r'^api/companies/(?P<company_id>[0-9]+)/edit$', views.company_edit_api.as_view(), name='company_edit_api'),
    url(r'^api/companies/new_company$', views.create_new_company_api.as_view(), name='create_new_company_api'),
    url(r'^api/companies$', views.companies_list_api.as_view(), name='companies_list_api'),

    url(r'^companies/(?P<company_id>[0-9]+)/linkedapps/(?P<app_id>[0-9]+)', views.company_linked_app_details, name='company_linked_app_details'),
    url(r'^companies/(?P<company_id>[0-9]+)/courses/(?P<course_id>.*)', views.company_course_details, name='company_course_details'),
    url(r'^companies/(?P<company_id>[0-9]+)/participants/(?P<user_id>[0-9]+)', views.company_participant_details_api.as_view(), name='company_participants_details'),
    url(r'^companies/(?P<company_id>[0-9]+)', views.company_details, name='company_details'),
    url(r'^companies', views.companies_list, name='companies_list'),
    url(r'^company_dashboard', views.company_dashboard, name='company_dashboard'),

    url(r'^api/cache/courses_list', cache_views.course_list_cached_api.as_view(), name='cache_views.course_list_cached_api'),
    url(r'^api/cache/organizations/(?P<organization_id>[0-9]+)/courses', cache_views.organization_courses_cached_api.as_view(), name='cache_views.organization_courses_cached_api'),
    url(r'^api/cache/organizations$', cache_views.organizations_list_cached_api.as_view(), name='cache_views.organizations_list_cached_api'),

    url(r'^api/tags/(?P<tag_id>[0-9]+)', views.tag_details_api.as_view(), name='tag_details_api'),
    url(r'^api/tags$', views.tags_list_api.as_view(), name='tags_list_api'),

    url(r'^api/admin_bulk_task', views.BulkTaskAPI.as_view(), name='bulk_task_api'),

    url(r'^permissions/(?P<user_id>[0-9]+)/edit', views.edit_permissions, name='edit_permissions'),
    url(r'^permissions', views.permissions, name='permissions'),

    url(r'^project/(?P<project_id>.*)/activity/(?P<activity_id>.*)/generate_assignments', views.generate_assignments, name='generate_assignments'),

    url(r'^api/s3file', s3views.s3file_api.as_view(), name='s3file_api'),

    url(r'^api/email-templates$', views.email_templates_get_and_post_api.as_view(), name='email_templates_get_and_post_api'),
    url(r'^api/email-templates/(?P<pk>[0-9]+)$', views.email_templates_put_and_delete_api.as_view(), name='email_templates_put_and_delete_api'),
    url(r'^api/email', views.email_send_api.as_view(), name='email_send_api'),
    url(r'^certificates/template_assets$', certificate_views.certificate_template_assets, name='certificate_template_assets'),
    url(r'^certificates/templates$', certificate_views.certificate_templates, name='certificate_templates'),
    url(r'^certificates/templates/new$', certificate_views.new_certificate_template, name='new_certificate_template'),
    url(r'^certificates/templates/(?P<template_id>\d+)/edit$', certificate_views.edit_certificate_template, name='edit_certificate_template'),

    url(r'^manager/', include('manager_dashboard.urls'), name='manager_dashboard_urls'),
]
