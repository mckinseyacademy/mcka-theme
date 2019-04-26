from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.courses, name='courses'),
    url(r'lessons_count/$', views.course_lessons_count, name='course_lessons_count'),
    url(r'courses_menu/$', views.courses_menu, name='courses_menu'),
    url(r'^(?P<course_id>.*)/course_lessons_menu$', views.course_lessons_menu, name='course_lessons_menu'),
    url(
        r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/module/(?P<page_id>.*)$',
        views.navigate_to_lesson_module,
        name='navigate_to_lesson_module'
    ),
    url(r'^(?P<course_id>.*)/overview$', views.course_overview, name='course_overview'),
    url(r'^(?P<course_id>.*)/announcements$', views.course_news, name='course_news'),
    url(r'^(?P<course_id>.*)/progress-json$', views.get_user_progress_json, name='get_user_progress_json'),
    url(r'^(?P<course_id>.*)/grades-json$', views.get_user_gradebook_json, name='get_user_gradebook_json'),
    url(
        r'^(?P<course_id>.*)/gradebook-json$',
        views.get_user_complete_gradebook_json,
        name='get_user_complete_gradebook_json'
    ),
    url(r'^(?P<course_id>.*)/completion-json$', views.get_user_completion_json, name='get_user_completion_json'),
    url(
        r'^(?P<course_id>.*)/progress-old/(?P<user_id>.*)$',
        views.course_user_progress,
        name='course_user_progress_old'
    ),
    url(r'^(?P<course_id>.*)/progress-old$', views.course_progress, name='course_progress'),
    url(r'^(?P<course_id>.*)/progress/(?P<user_id>.*)$', views.course_user_progress_v2, name='course_user_progress'),
    url(r'^(?P<course_id>.*)/progress$', views.course_progress_v2, name='course_progress'),
    url(r'^(?P<course_id>.*)/cohort$', views.course_cohort, name='course_cohort'),
    url(r'^(?P<course_id>.*)/syllabus$', views.course_syllabus, name='course_syllabus'),
    url(r'^(?P<course_id>.*)/resources$', views.course_resources, name='course_resources'),
    url(
        r'^(?P<course_id>.*)/lessons/jump_to_page/(?P<page_id>.*)$',
        views.infer_page_navigation,
        name='infer_page_navigation'
    ),
    url(
        r'^(?P<course_id>.*)/discussion/forum/users/(?P<user_id>\d+)/?$',
        views.course_discussion_userprofile,
        name='course_discussion_userprofile'
    ),
    url(
        r'^(?P<course_id>.*)/discussion/(?P<discussion_id>[\w\-.]+)/threads/(?P<thread_id>\w+)$',
        views.course_discussion,
        name='course_discussion'
    ),
    url(
        r'^(?P<course_id>.*)/discussion',
        views.course_discussion,
        name='course_discussion'
    ),  # should NOT end with $ - Backbone routing starts there
    url(
        r'^(?P<course_id>.*)/group_work/(?P<workgroup_id>.*)$',
        views.workgroup_course_group_work,
        name='workgroup_course_group_work'
    ),
    url(r'^(?P<course_id>.*)/group_work$', views.user_course_group_work, name='user_course_group_work'),
    url(r'^(?P<course_id>.*)/notready$', views.course_notready, name='course_notready'),
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/notes/?$', views.add_lesson_note, name='add_lesson_note'),
    url(
        r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)$',
        views.infer_chapter_navigation,
        name='infer_chapter_navigation'
    ),
    url(r'^(?P<course_id>.*)/notes/?$', views.course_notes, name='course_notes'),
    url(r'^(?P<course_id>.*)/export_notes/?$', views.course_export_notes, name='course_export_notes'),
    url(r'^(?P<course_id>.*)/lessons$', views.infer_course_navigation, name='infer_course_navigation'),
    url(r'^(?P<course_id>.*)/teaching_assistant$', views.contact_ta, name='contact_ta'),
    url(r'^(?P<course_id>.*)/article/?$', views.course_article, name='course_article'),
    url(r'^(?P<course_id>.*)/feature_flag/?$', views.course_feature_flag, name='course_feature_flag'),
    url(r'^(?P<course_id>.*)/group_member_email/(?P<group_id>.*)$', views.contact_member, name='contact_member'),
    url(r'^(?P<course_id>.*)/group_email/(?P<group_id>.*)$', views.contact_group, name='contact_group'),
    url(
        r'^(?P<course_id>.*)/group_submission_notify/(?P<group_id>.*)$',
        views.notify_group_on_submission,
        name='notify_group_on_submission'
    ),
    url(r'^(?P<course_id>.*)/$', views.course_landing_page, name='course_landing_page'),
    url(r'^(?P<course_id>.*)$', views.course_landing_page, name='course_landing_page'),
    url(r'^$', views.infer_default_navigation, name='infer_default_navigation'),
]
