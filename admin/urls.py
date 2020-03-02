from django.urls import path, re_path, include
from rest_framework.routers import SimpleRouter

from admin import views
from admin import cache as cache_views
from admin import s3 as s3views
from certificates import views as certificate_views

router = SimpleRouter()
router.register(r'^api/mobileapps', views.MobileAppsApi, basename='mobileapps_api')

urlpatterns = router.urls
urlpatterns += [
    path('', views.home, name='admin_home'),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/(?P<user_id>[0-9]+)/unenroll$',
        views.client_admin_unenroll_participant, name='client_admin_unenroll'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/(?P<user_id>[0-9]+)/edit-email$',
        views.client_admin_edit_email, name='client_admin_edit_email'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants/email_not_started$',
        views.client_admin_email_not_started, name='client_admin_email_not_started'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/download_course_report$',
        views.client_admin_download_course_report, name='download_course_report'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/participants$',
        views.client_admin_course_participants, name='client_admin_course_participants'
    ),

    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding/reset$',
        views.client_admin_branding_settings_reset, name='client_admin_branding_settings_reset'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding$',
        views.client_admin_branding_settings, name='client_admin_branding_settings'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/branding/create_edit$',
        views.client_admin_branding_settings_create_edit, name='client_admin_branding_settings_create_edit'
    ),

    # Learner dashboard urls
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/branding_reset$',
        views.course_learner_dashboard_branding_reset, name='course_learner_dashboard_branding_reset'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/branding$',
        views.course_learner_dashboard_branding, name='course_learner_dashboard_branding'
    ),

    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/discover/list$',
        views.course_learner_dashboard_discover_list, name='course_learner_dashboard_discover_list'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/discover/create$',
        views.course_learner_dashboard_discover_create_edit, name='course_learner_dashboard_discover_create_edit'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/discover/edit/(?P<discovery_id>.*)$',
        views.course_learner_dashboard_discover_create_edit, name='course_learner_dashboard_discover_create_edit'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/discover/delete/(?P<discovery_id>.*)$',
        views.course_learner_dashboard_discover_create_edit, name='course_learner_dashboard_discover_create_edit'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/discover/list/reorder$',
        views.course_learner_dashboard_discover_reorder, name='course_learner_dashboard_discover_reorder'
    ),

    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/duplicate/'
        r'(?P<copy_to_course_id>.+)$',
        views.course_learner_dashboard_copy,
        name='course_learner_dashboard_copy'
    ),

    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/tile/(?P<tile_id>.*)$',
        views.course_learner_dashboard_tile, name='course_learner_dashboard_tile'
    ),
    re_path(
        r'^courses/(?P<course_id>.+)/learner_dashboard/(?P<learner_dashboard_id>.+)/element_reorder$',
        views.course_learner_dashboard_tile_reorder, name='course_learner_dashboard_tile_reorder'
    ),
    re_path(
        r'^courses/(?P<course_id>.*)/learner_dashboard',
        views.course_learner_dashboard, name='course_learner_dashboard'
    ),
    # Learner dashboard urls

    # Demo registration CMS urls
    path('course_runs/', views.course_run_list, name='course_run_list'),
    path(
        'course_run/view/<int:course_run_id>/',
        views.course_run_view, name='course_run_view'
    ),
    path('course_run/create/', views.course_run_create_edit, name='course_run_create_edit'),
    path(
        'course_run/create/<int:course_run_id>',
        views.course_run_create_edit, name='course_run_create_edit'
    ),
    path(
        'course_run/csv_download/<int:course_run_id>/',
        views.course_run_csv_download, name='course_run_csv_download'
    ),
    path(
        'course_run/edit', views.EditAndDeleteSelfRegRole.as_view(),
        name='edit_and_delete_self_reg_role'
    ),

    # Demo registration CMS urls

    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/analytics/participant$',
        views.client_admin_course_analytics_participants, name='client_admin_course_analytics_participants'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/analytics/progress$',
        views.client_admin_course_analytics_progress, name='client_admin_course_analytics_progress'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/analytics$',
        views.client_admin_course_analytics, name='client_admin_course_analytics'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/status$',
        views.client_admin_course_status, name='client_admin_course_status'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)/users/(?P<user_id>[0-9]+)/progress$',
        views.client_admin_user_progress, name='client_admin_user_progress'
    ),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]+)/courses/(?P<course_id>.+)$',
        views.client_admin_course, name='client_admin_course'
    ),
    re_path(
        r'^client-admin/programs/(?P<program_id>.+)/download_program_report',
        views.client_admin_download_program_report, name='download_program_report'
    ),
    path('client-admin/programs', views.client_admin_program_detail, name='client_admin_program_detail'),
    path('client-admin/contact', views.client_admin_contact, name='client_admin_contact'),
    re_path(
        r'^client-admin/(?P<client_id>[0-9]*)', views.client_admin_home, name='client_admin_home'
    ),

    re_path(
        r'^api/courses/(?P<course_id>.*)/edit_course_meta_data/$', views.CourseMetaDataApiView.as_view(),
        name='course_meta_data_api_view'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.*)/blocks/$',
        views.CourseDetailsBlocksAPI.as_view(), name='course_details_blocks_api'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.*)/stats/$',
        views.course_details_stats_api.as_view(), name='course_details_stats_api'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.*)/engagement/$',
        views.course_details_engagement_api.as_view(), name='course_details_engagement_api'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.*)/performance/$',
        views.course_details_performance_api.as_view(), name='course_details_performance_api'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.*)/timeline/$',
        views.course_details_cohort_timeline_api.as_view(), name='course_details_cohort_timeline_api'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.*)/tags$',
        views.course_details_tags_api.as_view(), name='course_details_tags_api'
    ),
    re_path(
        r'^api/courses/(?P<course_id>.+)$', views.CourseDetailsApi.as_view(), name='course_details_api'
    ),
    path('api/courses', views.courses_list_api.as_view(), name='courses_list_api'),
    re_path(
        r'^courses/(?P<course_id>.*)/download_course_stats/$',
        views.download_course_stats, name='download_course_stats'
    ),
    path(
        'download_task_generated_csv/<slug:task_id>/',
        views.download_task_generated_csv, name='download_task_generated_csv'
    ),
    re_path(r'^courses/(?P<course_id>.*)/$', views.course_details, name='course_details'),
    path('courses/', views.courses_list, name='courses_list'),

    path('course-meta-content', views.course_meta_content_course_list, name='course_meta_content_course_list'),
    re_path(
        r'^course-meta-content/items/(?P<course_id>.+)$',
        views.course_meta_content_course_items, name='course_meta_content_course_items'
    ),
    path(
        'course-meta-content/item/new',
        views.course_meta_content_course_item_new, name='course_meta_content_course_item_new'
    ),
    path(
        'course-meta-content/item/<int:item_id>/edit',
        views.course_meta_content_course_item_edit, name='course_meta_content_course_item_edit'
    ),
    path(
        'course-meta-content/item/<int:item_id>/delete',
        views.course_meta_content_course_item_delete, name='course_meta_content_course_item_delete'
    ),

    re_path(r'^not_authorized', views.not_authorized, name='not_authorized'),

    path(
        'api/clients/<int:client_id>/download_student_list',
        views.download_student_list_api.as_view(), name='download_student_list_api'
    ),
    path('clients/client_new', views.client_new, name='client_new'),
    path('clients/<int:client_id>/edit', views.client_edit, name='client_edit'),
    path('clients/<int:client_id>', views.client_detail, name='client_detail'),
    re_path(
        r'^clients/(?P<client_id>[0-9]+)/upload_student_list/check/(?P<task_key>.*)$',
        views.upload_student_list_check, name='upload_student_list_check'
    ),
    path('clients/<int:client_id>/upload_student_list', views.upload_student_list, name='upload_student_list'),
    re_path(
        r'^clients/(?P<client_id>[0-9]+)/mass_student_enroll/check/(?P<task_key>.*)$',
        views.mass_student_enroll_check, name='mass_student_enroll_check'
    ),
    path('clients/<int:client_id>/mass_student_enroll', views.mass_student_enroll, name='mass_student_enroll'),
    path(
        'clients/<int:client_id>/change_company_image',
        views.change_company_image, name='change_company_image'
    ),
    path(
        'clients/<int:client_id>/upload_company_image',
        views.upload_company_image, name='upload_company_image'
    ),
    path('clients/<int:client_id>/image/edit', views.company_image_edit, name='company_image_edit'),
    path('clients/new/change_company_image', views.change_company_image, name='change_company_image'),
    path('clients/new/upload_company_image', views.upload_company_image, name='upload_company_image'),
    path('clients/new/image/edit', views.company_image_edit, name='company_image_edit'),
    path(
        'clients/<int:client_id>/download_student_list',
        views.download_student_list, name='download_student_list'
    ),
    path('clients/<int:client_id>/program_association', views.program_association, name='program_association'),
    path(
        'clients/<int:client_id>/add_students_to_program',
        views.add_students_to_program, name='add_students_to_program'
    ),
    path(
        'clients/<int:client_id>/add_students_to_course',
        views.add_students_to_course, name='add_students_to_course'
    ),
    path(
        'clients/<int:client_id>/user/<int:user_id>/resend',
        views.client_resend_user_invite, name='client_resend_user_invite'
    ),
    path(
        'clients/<int:client_id>/contact/add',
        views.client_detail_add_contact, name='client_detail_add_contact'
    ),
    path(
        'clients/<int:client_id>/contact/<int:user_id>/remove',
        views.client_detail_remove_contact, name='client_detail_remove_contact'
    ),
    re_path(r'^clients/(?P<client_id>[0-9]+)/contact', views.client_detail_contact, name='client_detail_contact'),
    re_path(
        r'^clients/(?P<client_id>[0-9]+)/navigation',
        views.client_detail_navigation, name='client_detail_navigation'
    ),
    re_path(
        r'^clients/(?P<client_id>[0-9]+)/(?P<img_type>[a-z]+)/edit_client_mobile_image$',
        views.edit_client_mobile_image, name='edit_client_mobile_image'
    ),
    path('clients/<int:client_id>/nav_links', views.client_detail_nav_links, name='client_detail_nav_links'),
    re_path(
        r'^clients/(?P<client_id>[0-9]+)/remove_image',
        views.remove_client_branding_image,
        name='remove_client_branding_image'
    ),
    path(
        'clients/<int:client_id>/customization',
        views.client_detail_customization, name='client_detail_customization'
    ),
    path('clients/<int:client_id>/sso/create-access-key', views.create_access_key, name='create_access_key'),
    path(
        'clients/<int:client_id>/sso/course-create-api',
        views.create_course_access_key_api.as_view(), name='create_course_access_key_api'
    ),
    path(
        'clients/<int:client_id>/sso/course-create',
        views.create_course_access_key, name='create_course_access_key'
    ),
    path(
        'clients/<int:client_id>/sso/<int:access_key_id>/share',
        views.share_access_key, name='share_access_key'
    ),
    re_path(r'^clients/(?P<client_id>[0-9]+)/sso', views.client_sso, name='client_sso'),
    re_path(r'^clients/(?P<client_id>[0-9]+)/(?P<detail_view>.*)', views.client_detail, name='client_detail'),
    re_path(r'^clients', views.client_list, name='client_list'),

    path('programs/program_new', views.ProgramView.as_view(), name='program_new'),
    path('programs/<int:program_id>/edit', views.ProgramView.as_view(), name='program_edit'),
    path('programs/<int:program_id>', views.program_detail, name='program_detail'),
    re_path(r'^programs/(?P<program_id>[0-9]+)/add_courses', views.add_courses, name='add_courses'),
    path(
        'programs/<int:program_id>/download_program_report',
        views.download_program_report, name='download_program_report'
    ),
    re_path(r'^programs/(?P<program_id>[0-9]+)/(?P<detail_view>.*)', views.program_detail, name='program_detail'),
    re_path(r'^programs', views.program_list, name='program_list'),

    path('workgroup/dashboard', views.groupwork_dashboard, name='groupwork_dashboard'),
    re_path(
        r'^workgroup/dashboard/my_links/(?:(?P<link_id>\d+)/)?$', views.QuickLinkView.as_view(),
        name='groupwork_dashboard_links'
    ),
    path(
        'workgroup/dashboard/programs/<int:program_id>/courses',
        views.groupwork_dashboard_courses, name='groupwork_dashboard_courses'
    ),
    path('workgroup/dashboard/companies', views.groupwork_dashboard_companies, name='groupwork_dashboard_companies'),
    re_path(
        r'^workgroup/dashboard/courses/(?P<course_id>.*)/projects$',
        views.groupwork_dashboard_projects, name='groupwork_dashboard_projects'
    ),
    re_path(
        r'^workgroup/dashboard/programs/(?P<program_id>.*)/courses/(?P<course_id>.*)/projects/'
        r'(?P<project_id>.*)/details$',
        views.groupwork_dashboard_details,
        name='groupwork_dashboard_details'
    ),
    path(
        'workgroup/dashboardV2/companies',
        views.groupwork_dashboard_companiesV2, name='groupwork_dashboard_companies'
    ),
    path('workgroup/dashboardV2', views.groupwork_dashboardV2, name='groupwork_dashboardV2'),
    re_path(
        r'^workgroup/course/(?P<course_id>.*)/download_group_list',
        views.download_group_list, name='download_group_list'
    ),
    re_path(
        r'^workgroup/course/(?P<course_id>.*)/download_group_projects_report',
        views.download_group_projects_report, name='download_group_projects_report'
    ),
    re_path(
        r'^workgroup/course/(?P<course_id>.*)/group_work_status/(?P<group_id>.*)',
        views.group_work_status, name='group_work_status'
    ),
    re_path(
        r'^workgroup/course/(?P<course_id>.*)/group_work_status',
        views.group_work_status, name='group_work_status'
    ),
    re_path(
        r'^workgroup/course/(?P<course_id>.*)/detail/(?P<workgroup_id>.*)',
        views.workgroup_detail, name='workgroup_detail'
    ),
    re_path(
        r'^workgroup/course/(?P<course_id>.*)/assignments',
        views.workgroup_course_assignments, name='workgroup_course_assignments'
    ),
    re_path(r'^workgroup/course/(?P<course_id>.*)', views.workgroup_course_detail, name='workgroup_course_detail'),
    path('workgroup/programs/list', views.workgroup_programs_list, name='workgroup_programs_list'),
    re_path(
        r'^workgroup/group/update/(?P<group_id>[0-9]+)/(?P<course_id>.*)',
        views.workgroup_group_update, name='workgroup_group_update'
    ),
    re_path(r'^workgroup/group/create/(?P<course_id>.*)', views.workgroup_group_create, name='workgroup_group_create'),
    path('workgroup/group/<int:group_id>/remove', views.workgroup_group_remove, name='workgroup_group_remove'),
    re_path(
        r'^workgroup/project/create/(?P<course_id>.*)',
        views.workgroup_project_create, name='workgroup_project_create'
    ),
    path(
        'workgroup/project/<int:project_id>/delete',
        views.workgroup_remove_project, name='workgroup_remove_project'
    ),
    re_path(r'^workgroup', views.workgroup_list, name='workgroup_list'),

    path(
        'api/participants/<int:user_id>/active_courses/export_stats',
        views.download_active_courses_stats, name='download_active_courses_stats'
    ),
    path(
        'api/participants/<int:user_id>/course_history/export_stats',
        views.download_course_history_stats, name='download_course_history_stats'
    ),
    path('api/participants/<int:user_id>', views.participant_details_api.as_view(), name='participant_details'),
    path(
        'api/participants/<int:user_id>/active_courses',
        views.participant_details_active_courses_api.as_view(), name='participant_details_active_courses_api'
    ),
    path(
        'api/participants/<int:user_id>/course_history',
        views.participant_details_course_history_api.as_view(), name='participant_details_course_history_api'
    ),
    re_path(
        r'^api/participants/(?P<user_id>[0-9]+)/course_manage/(?P<course_id>.+)$',
        views.participant_course_manage_api.as_view(), name='participant_course_manage_api'
    ),
    path(
        'api/participants/<int:user_id>/admin_companies',
        views.users_company_admin_get_post_put_delete_api.as_view(),
        name='users_company_admin_get_post_put_delete_api'
    ),
    path('api/participants/organizations', views.manage_user_company_api.as_view(), name='manage_user_company_api'),
    path('api/participants/courses', views.manage_user_courses_api.as_view(), name='manage_user_courses_api'),
    path(
        'api/participants/validate_participant_email/',
        views.validate_participant_email, name='validate_participant_email'
    ),
    path(
        'api/participants/validate_participant_username/',
        views.validate_participant_username, name='validate_participant_username'
    ),
    path(
        'api/participants/import_participants/download_activation_links/',
        views.download_activation_links_by_task_key, name='download_activation_links_by_task_key'
    ),
    path('api/participants/import_participants', views.import_participants, name='import_participants'),
    path(
        'api/participants/enroll_participants_from_csv',
        views.ParticipantsEnrollmentFromCsv.as_view(), name='enroll_participants_from_csv'
    ),
    path(
        'api/participants/update_company_fields_from_csv',
        views.update_company_field_from_csv, name='update_company_fields_from_csv$'
    ),
    path(
        'api/participants/delete_participants_from_csv',
        views.DeleteParticipantsFromCsv.as_view(), name='delete_participants_from_csv'
    ),
    path(
        'api/participants/update_manager_from_csv', views.update_manager_from_csv,
        name='update_manager_from_csv$'
    ),
    path(
        'api/participants/import_progress', views.ParticipantsImportProgress.as_view(),
        name='participants_import_progress_api'
    ),
    path('api/participants', views.ParticipantsListApi.as_view(), name='participants_list_api'),
    re_path(
        r'^participants/(?P<user_id>[0-9]+)/courses/(?P<course_id>.*)/unenroll$',
        views.participant_details_courses_unenroll_api.as_view(), name='participant_details_courses_unenroll_api'
    ),
    re_path(
        r'^participants/(?P<user_id>[0-9]+)/courses/(?P<course_id>.*)/edit_status$',
        views.participant_details_course_edit_status_api.as_view(), name='participant_details_course_edit_status_api'
    ),
    path(
        'participants/<int:user_id>/resend_activation_link',
        views.participant_mail_activation_link, name='participant_mail_activation_link'
    ),
    path(
        'participants/<int:user_id>/reset_password',
        views.participant_password_reset, name='participant_password_reset'
    ),
    path('participants/<int:user_id>', views.participant_details_api.as_view(), name='participants_details'),
    path('participants/import_progress', views.participants_import_progress, name='participants_import_progress'),
    path('participants', views.participants_list, name='participants_list'),

    path(
        'api/companies/<int:company_id>/linkedapps',
        views.CompanyLinkedAppsApi.as_view(), name='company_linked_apps_api'
    ),
    path(
        'api/companies/<int:company_id>/courses',
        views.CompanyCoursesApi.as_view(), name='company_courses_api'
    ),
    path(
        'api/companies/<int:company_id>/fields',
        views.CompanyCustomFields.as_view(), name='company_custom_fileds_api'
    ),
    path('api/companies/<int:company_id>/edit', views.company_edit_api.as_view(), name='company_edit_api'),
    path('api/companies/new_company', views.create_new_company_api.as_view(), name='create_new_company_api'),
    path('api/companies', views.companies_list_api.as_view(), name='companies_list_api'),

    path(
        'companies/<int:company_id>/linkedapps/<int:app_id>',
        views.company_linked_app_details, name='company_linked_app_details'
    ),
    re_path(
        r'^companies/(?P<company_id>[0-9]+)/courses/(?P<course_id>.*)',
        views.company_course_details, name='company_course_details'
    ),
    path(
        'companies/<int:company_id>/participants/<int:user_id>',
        views.company_participant_details_api.as_view(), name='company_participants_details'
    ),
    path('companies/<int:company_id>', views.CompanyDetailsView.as_view(), name='company_details'),
    path('companies', views.companies_list, name='companies_list'),
    re_path(r'^company_dashboard', views.company_dashboard, name='company_dashboard'),

    path(
        'api/cache/courses_list',
        cache_views.course_list_cached_api.as_view(), name='cache_views.course_list_cached_api'
    ),
    path(
        'api/cache/organizations/<int:organization_id>/courses',
        cache_views.organization_courses_cached_api.as_view(), name='cache_views.organization_courses_cached_api'
    ),
    path(
        'api/cache/organizations',
        cache_views.organizations_list_cached_api.as_view(), name='cache_views.organizations_list_cached_api'
    ),

    path('api/tags/<int:tag_id>', views.tag_details_api.as_view(), name='tag_details_api'),
    path('api/tags', views.tags_list_api.as_view(), name='tags_list_api'),

    re_path(r'^api/admin_bulk_task', views.BulkTaskAPI.as_view(), name='bulk_task_api'),

    path('permissions/<int:user_id>/edit', views.edit_permissions, name='edit_permissions'),
    re_path(r'^permissions', views.permissions, name='permissions'),

    re_path(
        r'^project/(?P<project_id>.*)/activity/(?P<activity_id>.*)/generate_assignments',
        views.generate_assignments, name='generate_assignments'
    ),

    path('api/s3file', s3views.s3file_api.as_view(), name='s3file_api'),

    path(
        'api/email-templates',
        views.email_templates_get_and_post_api.as_view(), name='email_templates_get_and_post_api'
    ),
    path(
        'api/email-templates/<int:pk>',
        views.email_templates_put_and_delete_api.as_view(), name='email_templates_put_and_delete_api'
    ),
    path('api/email', views.email_send_api.as_view(), name='email_send_api'),
    path(
        'certificates/template_assets',
        certificate_views.certificate_template_assets, name='certificate_template_assets'
    ),
    path('certificates/templates', certificate_views.certificate_templates, name='certificate_templates'),
    path('certificates/templates/new', certificate_views.new_certificate_template, name='new_certificate_template'),
    path(
        'certificates/templates/<int:template_id>/edit',
        certificate_views.edit_certificate_template, name='edit_certificate_template'
    ),

    path('manager/', include('manager_dashboard.urls'), name='manager_dashboard_urls'),

    # Cohorting
    re_path(
        r'^api/cohorts/courses/(?P<course_id>.+)/cohorts/(?P<cohort_id>.+)/users/(?P<username>.+)$',
        views.CohortUsers.as_view(), name='cohort_user_api'
    ),
    re_path(
        r'^api/cohorts/courses/(?P<course_id>.+)/cohorts/(?P<cohort_id>.+)/users',
        views.CohortUsers.as_view(), name='cohort_users_api'
    ),
    re_path(
        r'^api/cohorts/courses/(?P<course_id>.+)/cohorts/(?P<cohort_id>.+)$',
        views.CohortHandler.as_view(), name='cohort_list_api'
    ),
    re_path(
        r'^api/cohorts/courses/(?P<course_id>.+)/settings$',
        views.CohortSettings.as_view(), name='cohort_settings_api'
    ),
    re_path(r'^api/cohorts/courses/(?P<course_id>.+)/cohorts/$', views.CohortList.as_view(), name='cohort_list_api'),
    re_path(r'^api/cohorts/courses/(?P<course_id>.+)/users$', views.CohortImport.as_view(), name='cohort_import_api'),
    re_path(r'^cohorts/(?P<course_id>.*)/$', views.cohorts_course_details, name='cohorts_course_details'),

    # Problem Response Reports
    re_path(
        r'^api/problem_response_reports/course/(?P<course_id>.+)/$',
        views.ProblemResponseReportView.as_view(), name='course-reports'
    ),
]
