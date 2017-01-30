''' rendering templates from requests related to courses '''
import json
import csv
from datetime import datetime, timedelta
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseServerError

from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.template import loader, RequestContext

from admin.controller import load_course
from admin.models import (
    WorkGroup, LearnerDashboard, LearnerDashboardTile, LearnerDashboardDiscovery, 
    BrandingSettings, TileBookmark, LearnerDashboardTileProgress, LearnerDashboardBranding
    )
from admin.views import checked_course_access, AccessChecker
from api_client import course_api, user_api, workgroup_api
from api_client.api_error import ApiError
from api_client.group_api import PERMISSION_GROUPS
from api_client.user_api import USER_ROLES
from api_client.workgroup_models import Submission
from lib.authorization import permission_group_required
from lib.util import DottableDict
from main.models import CuratedContentItem

from .models import LessonNotesItem, FeatureFlags
from .controller import inject_gradebook_info, round_to_int, Proficiency, get_chapter_and_target_by_location, return_course_progress
from .controller import locate_chapter_page, load_static_tabs, load_lesson_estimated_time
from .controller import update_bookmark, group_project_reviews, add_months_to_date, progress_update_handler
from .controller import get_progress_leaders, get_proficiency_leaders, get_social_metrics, average_progress, choose_random_ta
from .controller import get_group_project_for_user_course, get_group_project_for_workgroup_course, group_project_location, createProgressObjects, _remove_duplicate_grader
from .user_courses import check_user_course_access, standard_data, load_course_progress, check_company_admin_user_access
from .user_courses import get_current_course_for_user, set_current_course_for_user, get_current_program_for_user, check_course_shell_access

# Create your views here.

_progress_bar_dictionary = {
    "normal": "#b1c2cc",
    "dropped": "#e5ebee",
    "group_work": "#66a5b5",
    "total": "#e37121",
    "proforma": "none",
}
if settings.PROGRESS_BAR_COLORS:
    _progress_bar_dictionary.update(settings.PROGRESS_BAR_COLORS)
PROGRESS_BAR_COLORS = DottableDict(_progress_bar_dictionary)

@login_required
@check_user_course_access
def course_landing_page(request, course_id):
    '''
    Course landing page for user for specified course
    etc. from user settings
    '''
    set_current_course_for_user(request, course_id)

    learner_dashboard = get_learner_dashboard(request, course_id)
    if learner_dashboard:
        redirect_url = '/learnerdashboard/' + str(learner_dashboard.id)
        return HttpResponseRedirect(redirect_url)

    static_tabs = load_static_tabs(course_id)
    course = standard_data(request).get("course", None)
    proficiency = course_api.get_course_metrics_grades(course_id, user_id=request.user.id, grade_object_type=Proficiency)
    load_lesson_estimated_time(course)
    social = get_social_metrics(course_id, request.user.id)
    gradebook = inject_gradebook_info(request.user.id, course)
    graded_items_count = sum(len(graded) for graded in course.graded_items().values())

    data = {
        "user": request.user,
        "course": course,
        "articles": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.ARTICLE).order_by('sequence')[:3],
        "videos": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.VIDEO).order_by('sequence')[:3],
        "tweet": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.TWEET).order_by('sequence').last(),
        "quote": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.QUOTE).order_by('sequence').last(),
        "infographic": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.IMAGE).order_by('sequence').last(),
        "proficiency": round_to_int(proficiency.user_grade_value * 100),
        "proficiency_graph": int(5 * round(proficiency.user_grade_value * 20)),
        "cohort_proficiency_average": proficiency.course_average_display,
        "cohort_proficiency_graph": int(5 * round(proficiency.course_average_value * 20)),
        "social": social,
        "average_progress": average_progress(course, request.user.id),
        "graded_items_count": graded_items_count,
    }
    return render(request, 'courses/course_main.haml', data)

def get_learner_dashboard(request, course_id):

    learner_dashboard = None

    if settings.LEARNER_DASHBOARD_ENABLED:
        try:
            feature_flags = FeatureFlags.objects.get(course_id=course_id)
            learner_dashboard_flag = feature_flags.learner_dashboard
        except:
            learner_dashboard_flag = None

        if learner_dashboard_flag:
            organizations = user_api.get_user_organizations(request.user.id)
            if len(organizations) > 0:
                organization = organizations[0]
                request.session['client_display_name'] = organization.display_name
                try:
                    learner_dashboard = LearnerDashboard.objects.get(course_id=course_id)
                except:
                    pass
    return learner_dashboard

@login_required
@check_user_course_access
def course_overview(request, course_id):
    overview = course_api.get_course_overview(course_id)
    data = {
        "overview": overview,
    }
    return render(request, 'courses/course_overview.haml', data)

@login_required
@check_user_course_access
def course_syllabus(request, course_id):
    data = {
        "syllabus": load_static_tabs(course_id, name="syllabus")
    }
    return render(request, 'courses/course_syllabus.haml', data)

@login_required
@check_user_course_access
def course_news(request, course_id):
    try:
        data = {
            "news": course_api.get_course_news(course_id)
        }
    except ApiError as e:
        # Handle 404 error as it indicates that no news is present
        if e.code != 404:
            raise
        data = {}

    return render(request, 'courses/course_news.haml', data)

@login_required
@check_user_course_access
def course_cohort(request, course_id):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    if feature_flags and not feature_flags.cohort_map:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    course = load_course(course_id, request=request)

    proficiency = get_proficiency_leaders(course_id, request.user.id)
    completions = get_progress_leaders(course_id, request.user.id)
    social = get_social_metrics(course_id, request.user.id)

    metrics = course_api.get_course_metrics(course_id)
    workgroups = user_api.get_user_workgroups(request.user.id, course_id)
    organizations = user_api.get_user_organizations(request.user.id)
    metrics.company_enrolled = 0
    metrics.group_enrolled = 0

    ta_user_json = json.dumps({})
    ta_user = choose_random_ta(course_id)
    if ta_user and hasattr(ta_user, 'to_json'):
        if not ta_user.title:
            ta_user.title = ''
        ta_user_json = ta_user.to_json()
    ta_user_id = ta_user.id if ta_user else None

    if len(organizations) > 0:
        organization = organizations[0]
        organizationUsers = {u['id']:u['username'] for u in course_api.get_course_details_users(course_id, {'page_size': 0, 'fields': 'id,username', 'organizations': organization.id})}
        metrics.company_enrolled = len(organizationUsers)
    metrics.groups_users = []
    if len(workgroups) > 0:
        workgroup = workgroup_api.get_workgroup(workgroups[0].id)
        metrics.group_enrolled = len(workgroup.users)
        if workgroup.users > 0:
            user_ids = [str(student.id) for student in workgroup.users]
            additional_fields = ["city", "title", "avatar_url", "full_name", "first_name", "last_name"]
            user_dict = {u.id : u for u in user_api.get_users(ids=user_ids,fields=additional_fields)}
            for student in workgroup.users:
                user = user_dict[student.id]
                if user.city and user.city != '' and ta_user_id != user.id:
                    if not user.title:
                        user.title = ''
                    metrics.groups_users.append(user.to_dict())
    metrics.groups_users = json.dumps(metrics.groups_users)

    metrics.cities = []
    cities = course_api.get_course_metrics_by_city(course_id)
    for city in cities:
        if city.city != '':
            metrics.cities.append({'city': city.city, 'count': city.count})
    metrics.cities = json.dumps(metrics.cities)

    user_roles = request.user.get_roles_on_course(course_id)
    is_observer = (len([r for r in user_roles if r.role==USER_ROLES.OBSERVER]) > 0)

    data = {
        'proficiency': proficiency,
        'completions': completions,
        'social': social,
        'metrics': metrics,
        'ta_user': ta_user_json,
        'ta_email': settings.TA_EMAIL_GROUP,
        'leaderboard_ranks': [1,2,3],
        'is_observer': is_observer,
    }
    return render(request, 'courses/course_cohort.haml', data)

def _render_group_work(request, course, project_group, group_project, learner_dashboard_id=None, flag_branding=None):

    seqid = request.GET.get("seqid", None)
    if seqid and " " in seqid:
        seqid = seqid.replace(" ", "+")

    select_stage = request.GET.get('select_stage', None)

    if group_project is not None:
        activity, vertical_usage_id = group_project_location(group_project, seqid)
    else:
        activity = vertical_usage_id = None

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN
    lms_port = settings.LMS_PORT

    ta_user = choose_random_ta(course.id)

    notify_group_on_submission_url = "/"
    if course and project_group:
        notify_group_on_submission_url = reverse('notify_group_on_submission', args=[course.id, project_group.id])
    data = {
        "lesson_content_parent_id": "course-group-work",
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "course_id": course.id,
        "legacy_course_id": course.id,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "lms_port": lms_port,
        "use_current_host": getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True),
        "project_group": project_group,
        "group_project": group_project,
        "current_activity": activity,
        "ta_user": ta_user,
        "group_work_url": request.path_info,
        "notify_group_on_submission_url": notify_group_on_submission_url
    }
    if select_stage:
        data['select_stage'] = select_stage

    feature_flags = FeatureFlags.objects.filter(course_id=course.id)
    if len(feature_flags) > 0:
        if feature_flags[0].learner_dashboard and learner_dashboard_id is None:
            try:
                learner_dashboard_id = LearnerDashboard.objects.get(course_id=course.id).id
                redirect_url = "/learnerdashboard/" + str(learner_dashboard_id) + request.get_full_path()
                return HttpResponseRedirect(redirect_url)
            except:
                pass

    if learner_dashboard_id:

        try:
            learner_dashboard = LearnerDashboard.objects.get(pk=learner_dashboard_id)
        except:
            return HttpResponse(status=404)

        calendar_items = LearnerDashboardTile.objects.filter(learner_dashboard=learner_dashboard_id, show_in_calendar=True)

        data.update({
            "learner_dashboard": learner_dashboard,
            "calendar_enabled": True if calendar_items else False,
            "course_id": course.id,
        })

        if learner_dashboard.course_id == course.id:
            if flag_branding:
                try:
                    data['branding'] = LearnerDashboardBranding.objects.get(learner_dashboard=learner_dashboard_id)
                except:
                    pass

        return render(request, 'courses/course_group_work_ld.haml', data)
    else:
        return render(request, 'courses/course_group_work.haml', data)

@login_required
@check_user_course_access
def user_course_group_work(request, course_id):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    if feature_flags and not feature_flags.group_work:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    # remove this in case we are a TA who is taking a course themselves
    user_api.delete_user_preference(request.user.id, "TA_REVIEW_WORKGROUP")

    course = load_course(course_id, request=request)
    project_group, group_project = get_group_project_for_user_course(request.user.id, course)
    set_current_course_for_user(request, course_id)

    return _render_group_work(request, course, project_group, group_project)

@login_required
def user_course_group_work_learner_dashboard(request, learner_dashboard_id, course_id):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    if feature_flags and not feature_flags.group_work:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    # remove this in case we are a TA who is taking a course themselves
    user_api.delete_user_preference(request.user.id, "TA_REVIEW_WORKGROUP")

    course = load_course(course_id, request=request)
    project_group, group_project = get_group_project_for_user_course(request.user.id, course)
    set_current_course_for_user(request, course_id)

    return _render_group_work(request, course, project_group, group_project, learner_dashboard_id, feature_flags.branding)

@login_required
@permission_group_required(PERMISSION_GROUPS.MCKA_TA)
def workgroup_course_group_work(request, course_id, workgroup_id, learner_dashboard_id=None):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    branding_flag = None
    if feature_flags and not feature_flags.group_work:
        return HttpResponseRedirect('/courses/{}'.format(course_id))
    if feature_flags and feature_flags.group_work:
        branding_flag = feature_flags.branding

    # set this workgroup as the preference for reviewing
    user_api.set_user_preferences(request.user.id, {"TA_REVIEW_WORKGROUP": workgroup_id})

    course = load_course(course_id, request=request)
    project_group, group_project = get_group_project_for_workgroup_course(workgroup_id, course)

    return _render_group_work(request, course, project_group, group_project, learner_dashboard_id, branding_flag)

def _course_discussion_data(request, course_id):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    if feature_flags and not feature_flags.discussions:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    course = load_course(course_id, request=request)
    has_course_discussion = False
    vertical_usage_id = None

    # Locate the first chapter page
    if course.discussion and \
       course.discussion.sequentials and \
       course.discussion.sequentials[0].pages:
        has_course_discussion = True
        vertical_usage_id = course.discussion.sequentials[0].pages[0].vertical_usage_id()

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN
    lms_port = settings.LMS_PORT

    mcka_ta = choose_random_ta(course_id)

    return {
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "has_course_discussion": has_course_discussion,
        "course_id": course_id,
        "legacy_course_id": course_id,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "lms_port": lms_port,
        "use_current_host": getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True),
        "mcka_ta": mcka_ta,
        "flag_branding": feature_flags.branding
    }

@login_required
def course_discussion_learner_dashboard(request, learner_dashboard_id, course_id):

    data = _course_discussion_data(request, course_id)

    try:
        learner_dashboard = LearnerDashboard.objects.get(pk=learner_dashboard_id)
    except:
        return HttpResponse(status=404)

    if learner_dashboard.course_id == course_id:
        if data['flag_branding']:
            try:
                data['branding'] = LearnerDashboardBranding.objects.get(learner_dashboard=learner_dashboard_id)
            except:
                pass

    calendar_items = LearnerDashboardTile.objects.filter(learner_dashboard=learner_dashboard_id, show_in_calendar=True)

    data.update({
        "learner_dashboard": learner_dashboard,
        "calendar_enabled": True if calendar_items else False,
        "course_id": course_id,
    })

    return render(request, 'courses/course_discussion_ld.haml', data)

@login_required
@check_user_course_access
def course_discussion(request, course_id):
    data = _course_discussion_data(request, course_id)
    return render(request, 'courses/course_discussion.haml', data)

@login_required
def course_discussion_userprofile(request, course_id, user_id):

    data = {
        "course_id": course_id,
    }
    return render(request, 'courses/course_discussion_userprofile.haml', data)

def _course_progress_for_user(request, course_id, user_id):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    if feature_flags and not feature_flags.progress_page:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    course = load_course(course_id, request=request)
    progress_user = user_api.get_user(user_id)

    # add in all the grading information
    gradebook = inject_gradebook_info(user_id, course)

    graders = gradebook.grading_policy.GRADER
    for grader in graders:
        grader.weight = round_to_int(grader.weight*100)

    cutoffs = gradebook.grading_policy.GRADE_CUTOFFS
    pass_grade = round_to_int(cutoffs.get(min(cutoffs, key=cutoffs.get)) * 100)

    workgroup_avg_sections = [section for section in gradebook.courseware_summary if section.display_name.startswith(settings.GROUP_PROJECT_IDENTIFIER)]

    project_group, group_project = get_group_project_for_user_course(user_id, course)
    if project_group and group_project:
        group_activities, group_work_avg = group_project_reviews(user_id, course_id, project_group, group_project)

        # format scores & grades
        for activity in group_activities:
            if hasattr(activity, 'due_upon'):
                activity.due_on = activity.due_upon
            else:
                activity.due_on = activity.due.strftime("%B %e") if activity.due else ""
            if activity.score is not None:
                activity.score = round_to_int(activity.score)
            for i, grade in enumerate(activity.grades):
                if grade is not None:
                    activity.grades[i] = round_to_int(grade)
    else:
        group_activities = None
        group_work_avg = None

    bar_chart = [{'pass_grade': pass_grade, 'key': 'Lesson Scores', 'values': []}]

    section_breakdown = gradebook.grade_summary.section_breakdown
    categories = set([grade.category for grade in section_breakdown])

    # helper to determine is grade is "dropped" - definition of this may change and easy to replace in one location
    def is_dropped(grade):
        return hasattr(grade, 'mark')

    category_map = {}
    group_category = None
    has_values_for = DottableDict({})
    for category in categories:
        category_map[category] = [grade for grade in section_breakdown if grade.category == category]
        if category.startswith(settings.GROUP_PROJECT_IDENTIFIER):
            group_category = category

    for cat in [category for category in categories if category != group_category]:
        for grade in category_map[cat]:
            color = PROGRESS_BAR_COLORS.normal
            if is_dropped(grade):
                color = PROGRESS_BAR_COLORS.dropped
                has_values_for.dropped = True
            else:
                has_values_for.normal = True

            bar_chart[0]['values'].append({
               'label': grade.label,
               'value': grade.percent*100,
               'color': color,
            })

    activity_index = 0
    if group_category is not None:
        has_values_for.group_work = True
        for grade in category_map[group_category]:
            if not is_dropped(grade):
                label = grade.label
                # if group_activities and activity_index < len(group_activities):
                #     label = group_activities[activity_index].name
                bar_chart[0]['values'].append({
                   'label': label,
                   'value': grade.percent*100,
                   'color': PROGRESS_BAR_COLORS.group_work,
                })
                activity_index += 1

    total = round_to_int(gradebook.grade_summary.percent*100)
    bar_chart[0]['values'].append({
        'label': 'TOTAL',
        'value': total,
        'color': PROGRESS_BAR_COLORS.total
    })

    proforma_grade = round_to_int(gradebook.proforma_grade * 100)
    bar_chart[0]['values'].append({
        'value': proforma_grade,
        'color': PROGRESS_BAR_COLORS.proforma
    })

    data = {
        'bar_chart': json.dumps(bar_chart),
        'pass_grade': pass_grade,
        'graders': graders,
        'group_activities': group_activities,
        "average_progress": average_progress(course, user_id),
        "has_values_for": has_values_for,
        "progress_user": progress_user,
    }

    if progress_user.id != request.user.id:
        # Inject course progress for nav header
        load_course_progress(course, user_id)
        # Add index to lesson
        for idx, lesson in enumerate(course.chapters, start=1):
            lesson.index = idx

        data["course"] = course

    return render(request, 'courses/course_progress.haml', data)

def _course_progress_for_user_v2(request, course_id, user_id):
    feature_flags = FeatureFlags.objects.filter(course_id=course_id)
    if len(feature_flags) > 0:
        feature_flags = feature_flags[0]
    else:
        feature_flags = None
    if feature_flags and not feature_flags.progress_page:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    course = load_course(course_id, request=request)
    progress_user = user_api.get_user(user_id)
    social = get_social_metrics(course_id, user_id)
    proficiency = course_api.get_course_metrics_grades(course_id, user_id=user_id, grade_object_type=Proficiency)
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    course.group_work_enabled = feature_flags.group_work
    course_run = load_static_tabs(course_id, name="course run")

    if course_run:
        try:
            course.course_run = json.loads(course_run.content)
        except:
            pass

    # add in all the grading information
    gradebook = inject_gradebook_info(user_id, course)

    graders = gradebook.grading_policy.GRADER

    graders_weight_sum = 0

    for grader in graders:
        grader.weight = round_to_int(grader.weight*100)
        graders_weight_sum += grader.weight

    if graders_weight_sum > 100:
        _remove_duplicate_grader(graders)

    # add module completion
    completions = course_api.get_course_completions(course.id, user_id)
    completed_ids = [result.content_id for result in completions]
    for lesson in course.chapters:
        lesson_component_ids = course.lesson_component_ids(lesson.id, completed_ids,
                                                           settings.PROGRESS_IGNORE_COMPONENTS)

    cutoffs = gradebook.grading_policy.GRADE_CUTOFFS
    pass_grade = round_to_int(cutoffs.get(min(cutoffs, key=cutoffs.get)) * 100)
    completed_items_count = len([module for module in course.graded_items()["modules"] if getattr(module, 'is_complete', None)])

    project_group, group_project = get_group_project_for_user_course(user_id, course)
    if project_group and group_project:
        group_activities, group_work_avg = group_project_reviews(user_id, course_id, project_group, group_project)

        # format scores & grades
        for course_group_project in course.group_projects:
            if group_project.id != course_group_project.id:
                course.group_projects.remove(course_group_project)

        for activity in group_activities:
            if activity.is_graded and activity.score is not None:
                completed_items_count += 1
            if activity.score is not None:
                activity.score = round_to_int(activity.score)
            for i, grade in enumerate(activity.grades):
                if grade is not None:
                    activity.grades[i] = round_to_int(grade)
    else:
        group_activities = None
        group_work_avg = None

    graded_items_count = sum(len(graded) for graded in course.graded_items().values())
    data = {
        "social": social,
        "progress_user": progress_user,
        "proficiency": round_to_int(proficiency.user_grade_value * 100),
        "proficiency_graph": int(5 * round(proficiency.user_grade_value * 20)),
        "cohort_proficiency_average": proficiency.course_average_display,
        "cohort_proficiency_graph": int(5 * round(proficiency.course_average_value * 20)),
        "average_progress": average_progress(course, request.user.id),
        "completed_items_count": completed_items_count,
        "graded_items_count": graded_items_count,
        "graded_items_rows": graded_items_count + 1,
        "group_activities": group_activities,
        "graders": ', '.join("%s%% %s" % (grader.weight, grader.type_name) for grader in graders),
        "total_replies": social["metrics"].num_replies + social["metrics"].num_comments,
        "course_run": course_run,
        'feature_flags': feature_flags,
    }

    if progress_user.id != request.user.id:
        # Inject course progress for nav header
        load_course_progress(course, user_id)
        # Add index to lesson
        for idx, lesson in enumerate(course.chapters, start=1):
            lesson.index = idx

        data["course"] = course

    return render(request, 'courses/course_progress_v2.haml', data)

@login_required
@check_company_admin_user_access
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_SUBADMIN)
def course_user_progress(request, user_id, course_id):
    return _course_progress_for_user(request, course_id, user_id)

@login_required
@check_user_course_access
def course_progress(request, course_id):
    return _course_progress_for_user(request, course_id, request.user.id)

@login_required
@check_company_admin_user_access
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_SUBADMIN)
def course_user_progress_v2(request, user_id, course_id):
    return _course_progress_for_user_v2(request, course_id, user_id)

@login_required
@check_user_course_access
def course_progress_v2(request, course_id):
    return _course_progress_for_user_v2(request, course_id, request.user.id)

@login_required
@check_user_course_access
def course_resources(request, course_id):
    data = {
        "resources": load_static_tabs(course_id, name="resources")
    }
    return render(request, 'courses/course_resources.haml', data)

@login_required
def course_resources_learner_dashboard(request, learner_dashboard_id, course_id):
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    if feature_flags and not feature_flags.resources:
        return HttpResponseRedirect('/courses/{}'.format(course_id))

    try:
        learner_dashboard = LearnerDashboard.objects.get(pk=learner_dashboard_id)
    except:
        return HttpResponse(status=404)

    calendar_items = LearnerDashboardTile.objects.filter(learner_dashboard=learner_dashboard_id, show_in_calendar=True)

    data = {
        "resources": load_static_tabs(course_id, name="resources"),
        "course_id": course_id,
        "calendar_enabled": True if calendar_items else False,
        "learner_dashboard": learner_dashboard,
    }

    if learner_dashboard.course_id == course_id:
        if feature_flags.branding:
            try:
                data['branding'] = LearnerDashboardBranding.objects.get(learner_dashboard=learner_dashboard_id)
            except:
                pass

    return render(request, 'courses/course_resources_learner_dashboard.haml', data)

@login_required
@check_user_course_access
def navigate_to_lesson_module(request, course_id, chapter_id, page_id, tile_type=None, tile_id=None, learner_dashboard_id=None):

    ''' go to given page within given chapter within given course '''
    course = load_course(course_id, request=request)
    current_sequential = course.get_current_sequential(chapter_id, page_id)

    # Load the current program for this user
    program = get_current_program_for_user(request)

    data = {
        "user": request.user,
        "program": program,
        "lesson_content_parent_id": "course-lessons",
        "course_id": course_id,
        "legacy_course_id": course_id,
        "tile_type": tile_type,
        "tile_id": tile_id,
    }

    if not current_sequential.is_started:
        data["not_started_message"] = _("This lesson does not start until {}").format(current_sequential.start_upon)
        return render(request, 'courses/course_future_lesson.haml', data)

    # Take note that the user has gone here
    set_current_course_for_user(request, course_id)
    update_bookmark(
        request.user.id,
        course_id,
        chapter_id,
        current_sequential.id,
        page_id
    )

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN
    lms_port = settings.LMS_PORT

    data.update({
        "remote_session_key": remote_session_key,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "lms_port": lms_port,
        "use_current_host": getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True),
    })

    if request.is_ajax():
        try:
            progress_update_handler(request, course, chapter_id, page_id)
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=204)

    if learner_dashboard_id:

        try:
            learner_dashboard = LearnerDashboard.objects.get(pk=learner_dashboard_id)
        except:
            return HttpResponse(status=404)

        calendar_items = LearnerDashboardTile.objects.filter(learner_dashboard=learner_dashboard_id, show_in_calendar=True)

        data.update({
            "learner_dashboard": learner_dashboard,
            "calendar_enabled": True if calendar_items else False,
        })

        if learner_dashboard.course_id == course_id:
            try:
                feature_flags = FeatureFlags.objects.get(course_id=course_id)
                if feature_flags.branding:
                    try:
                        data['branding'] = LearnerDashboardBranding.objects.get(learner_dashboard=learner_dashboard)
                    except:
                        pass
            except:
                pass
        else:
            return render(request, 'courses/course_lessons_ld_external.haml', data)

        return render(request, 'courses/course_lessons_ld.haml', data)
    else:
        return render(request, 'courses/course_lessons.haml', data)


def course_notready(request, course_id):
    course = load_course(course_id, request=request)
    return render(request, 'courses/course_notready.haml', {"course": course})

@login_required
@check_user_course_access
def infer_chapter_navigation(request, course_id, chapter_id):
    '''
    Go to the bookmarked page for given chapter within given course
    If no chapter or course given, system tries to go to location within last
    visited course
    '''
    if not course_id:
        course_id = get_current_course_for_user(request)

    course_id, chapter_id, page_id = locate_chapter_page(
        request,
        request.user.id,
        course_id,
        chapter_id
    )

    if course_id and chapter_id and page_id:
        return HttpResponseRedirect('/courses/{}/lessons/{}/module/{}'.format(course_id, chapter_id, page_id))
    else:
        return HttpResponseRedirect('/courses/{}/notready'.format(course_id))

@login_required
@check_user_course_access
def infer_page_navigation(request, course_id, page_id):
    '''
    Go to the specified page
    If no course given, system tries to go to location within last visited course
    '''
    if not course_id:
        course_id = get_current_course_for_user(request)

    course = load_course(course_id, request=request)
    ta_grading_group = user_api.get_user_preferences(request.user.id).get("TA_REVIEW_WORKGROUP", None)
    project_group, group_project = get_group_project_for_user_course(request.user.id, course, ta_grading_group)
    chapter_id, vertical_id, final_target_id = get_chapter_and_target_by_location(request, course_id, page_id)

    if course_id and chapter_id and vertical_id:
        if 'learner_dashboard_id' in request.session and 'learnerdashboard' in request.META.get('HTTP_REFERER'):
            redirect_url = '/courses/{}/lessons/{}/module/{}'.format(course_id, chapter_id, vertical_id)
            if group_project and group_project.is_v2 and group_project.vertical_id == vertical_id:
                redirect_url = "/learnerdashboard/courses/{}/group_work".format(course_id)

            if final_target_id not in (chapter_id, vertical_id):
                redirect_url += '?activate_block_id={final_target_id}'.format(final_target_id=final_target_id)
        else:
            redirect_url = '/courses/{}/lessons/{}/module/{}'.format(course_id, chapter_id, vertical_id)
            if group_project and group_project.is_v2 and group_project.vertical_id == vertical_id:
                redirect_url = "/courses/{}/group_work".format(course_id)

                if ta_grading_group:
                    redirect_url += "/{ta_grading_group}".format(ta_grading_group=ta_grading_group)

            if final_target_id not in (chapter_id, vertical_id):
                redirect_url += '?activate_block_id={final_target_id}'.format(final_target_id=final_target_id)
    else:
        redirect_url = '/courses/{}/notready'.format(course_id)

    return HttpResponseRedirect(redirect_url)

def infer_course_navigation(request, course_id):
    ''' handler to call infer chapter nav with no chapter '''
    return infer_chapter_navigation(request, course_id, None)

def infer_default_navigation(request):
    ''' handler to call infer chapter nav with no course '''
    return infer_chapter_navigation(request, None, None)

@login_required
@check_user_course_access
def contact_ta(request, course_id):
    course = load_course(course_id, request=request)
    email_subject = "{} | {}".format(course.name, course.id)
    html_content = ""
    text_content = ""
    if request.POST["contact-from"] == "group-work":
        project_group, group_project = get_group_project_for_user_course(request.user.id, course)
        email_subject += " | {}".format(group_project.name)
        group_work_uri = request.build_absolute_uri().replace("/teaching_assistant", "/group_work")
        html_content = "<p><a href='{}'>{}</a></p>".format(group_work_uri, email_subject)
        text_content = group_work_uri + "\n"
    user = user_api.get_user(request.user.id)
    email_header_from = user.email
    email_from = "{}<{}>".format(
        user.formatted_name,
        settings.APROS_EMAIL_SENDER
    )
    timestamp = datetime.now().strftime('%b %d %Y %H:%M:%S')
    email_subject += " | {}".format(timestamp)
    email_to = settings.TA_EMAIL_GROUP
    email_message = request.POST["ta_message"]
    html_content += "<p>{}</p>".format(email_message)
    text_content += email_message
    try:
        email = EmailMultiAlternatives(email_subject, text_content, email_from, [email_to], headers = {'Reply-To': email_header_from})
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
    except:
        return HttpResponse(
        json.dumps({"message": _("Message not sent.")}),
        content_type='application/json'
    )
    return HttpResponse(
        json.dumps({"message": _("Message successfully sent.")}),
        content_type='application/json'
    )

@login_required
@check_user_course_access
def contact_group(request, course_id, group_id):
    user = user_api.get_user(request.user.id)
    email_header_from = user.email
    email_from = "{}<{}>".format(
        user.formatted_name,
        settings.APROS_EMAIL_SENDER
    )
    group = WorkGroup.fetch_with_members(group_id)
    students = group.members
    course = load_course(course_id)
    email_to = [student.email for student in students]
    email_content = request.POST["group_message"]
    email_subject = "Group Project Message - {}".format(course.name)
    try:
        email = EmailMessage(email_subject, email_content, email_from, email_to, headers = {'Reply-To': email_header_from})
        email.send(fail_silently=False)
    except:
        return HttpResponse(
        json.dumps({"message": _("Message not sent.")}),
        content_type='application/json'
    )
    return HttpResponse(
        json.dumps({"message": _("Message successfully sent.")}),
        content_type='application/json'
    )

@login_required
@check_user_course_access
def contact_member(request, course_id, group_id):
    user = user_api.get_user(request.user.id)
    email_header_from = user.email
    email_from = "{}<{}>".format(
        user.formatted_name,
        settings.APROS_EMAIL_SENDER
    )
    email_to = request.POST["member-email"]
    email_content = request.POST["member_message"]
    course = load_course(course_id)
    email_subject = "Group Project Message - {}".format(course.name) #just for testing

    group = WorkGroup.fetch_with_members(group_id)
    students = group.members
    group_emails = [student.email for student in students]

    if email_to in group_emails:
        try:
            email = EmailMessage(email_subject, email_content, email_from, [email_to], headers = {'Reply-To': email_header_from})
            email.send(fail_silently=False)
        except:
            return HttpResponse(
            json.dumps({"message": _("Message not sent.")}),
            content_type='application/json'
        )
        return HttpResponse(
            json.dumps({"message": _("Message successfully sent.")}),
            content_type='application/json'
        )
    else:
        return HttpResponse(
            json.dumps({"message": _("Message not sent. Email is not valid")}), #replace with another message
            content_type='application/json'
        )

@login_required
@check_user_course_access
def notify_group_on_submission(request, course_id, group_id):
    user = user_api.get_user(request.user.id)
    group = WorkGroup.fetch_with_members(group_id)
    submission_map = workgroup_api.get_latest_workgroup_submissions_by_id(group.id, Submission)
    submission_id = request.POST['submission_id']
    submission = submission_map.get(submission_id)
    if submission is None:
        return HttpResponseNotFound(
            json.dumps({"message": _("Submission not found.")}),
            content_type='application/json'
        )

    email_from = settings.APROS_EMAIL_SENDER
    email_to = [student.email for student in group.members]
    email_subject = _("We've received your submission!")
    email_content = _("Thank you for your group work submission. "
                      "We received {file_name} uploaded by {user_full_name} on {submission_dt}. "
                      "You may replace this file at any time before the group work deadline.").format(
                          file_name=submission.document_filename,
                          user_full_name=user.formatted_name,
                          submission_dt=submission.modified.strftime('%B %d, %I:%m %p')
                      )
    try:
        email = EmailMessage(email_subject, email_content, email_from, email_to)
        email.send(fail_silently=False)
    except:
        return HttpResponseServerError(
            json.dumps({"message": _("There was a problem; message not sent.")}),
            content_type='application/json'
        )
    return HttpResponse(
        json.dumps({"message": _("Message successfully sent.")}),
        content_type='application/json'
    )

@login_required
@check_user_course_access
def course_export_notes(request, course_id):
    course = load_course(course_id).inject_basic_data()
    notes = LessonNotesItem.objects.filter(user_id = request.user.id, course_id = course_id)

    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="mcka_course_notes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Created At', 'Course Name', 'Lesson Name', 'Module Name', 'Note'])

    for note in notes:
        writer.writerow(note.as_csv(course))

    return response

@login_required
@check_user_course_access
def course_notes(request, course_id):
    course = load_course(course_id).inject_basic_data()
    notes = LessonNotesItem.objects.filter(user_id = request.user.id, course_id = course_id)
    notes = [note.as_json(course) for note in notes]
    return HttpResponse(json.dumps(notes))

@require_POST
@login_required
@check_user_course_access
def add_lesson_note(request, course_id, chapter_id):
    course = load_course(course_id).inject_basic_data()

    note = LessonNotesItem(
        body = request.POST['body'],
        user_id = request.user.id,
        course_id = course_id,
        lesson_id = chapter_id,
        module_id = request.POST['module_id'],
    )
    note.save()

    return HttpResponse(json.dumps(note.as_json(course)))

@login_required
@check_user_course_access
def course_article(request, course_id):
    data = {
        "article": load_static_tabs(course_id, name="article")
    }
    return render(request, 'courses/course_article.haml', data)

@login_required
def course_learner_dashboard(request, learner_dashboard_id):

    if settings.LEARNER_DASHBOARD_ENABLED:
        try:
            learner_dashboard = LearnerDashboard.objects.get(pk=learner_dashboard_id)
            request.session['last_visited_course'] = learner_dashboard.course_id
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=403)

    check_course_shell_access(request, learner_dashboard.course_id)

    learner_dashboard_tiles = LearnerDashboardTile.objects.filter(learner_dashboard=learner_dashboard.id, show_in_dashboard=True).order_by('position')
    discovery_items = LearnerDashboardDiscovery.objects.filter(learner_dashboard=learner_dashboard.id).order_by('position')

    calendar_items = LearnerDashboardTile.objects.filter(learner_dashboard=learner_dashboard.id, show_in_calendar=True)

    try:
        bookmark = TileBookmark.objects.get(user=request.user.id)
    except:
        bookmark = None

    try:
        feature_flags = FeatureFlags.objects.get(course_id=learner_dashboard.course_id)
    except:
        feature_flags = []

    data = {
        'learner_dashboard': learner_dashboard,
        'learner_dashboard_tiles': learner_dashboard_tiles,
        'feature_flags': feature_flags,
        'discovery_items': discovery_items,
        'bookmark': bookmark,
        'calendar_enabled': True if calendar_items else False,
        'today': datetime.now(),
        'course_id': learner_dashboard.course_id
    }        

    if feature_flags and feature_flags.branding:
        try:
            learner_dashboard_branding = LearnerDashboardBranding.objects.get(learner_dashboard=learner_dashboard.id)
            data['branding'] = learner_dashboard_branding
        except:
            pass

    return render(request, 'courses/course_learner_dashboard.haml', data)

@require_POST
@login_required
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_SUBADMIN)
#@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def course_feature_flag(request, course_id, restrict_to_courses_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
    feature_flags = FeatureFlags.objects.get(course_id=course_id)
    feature_flags.group_work = request.POST.get('group_work', None) == 'on'
    feature_flags.discussions = request.POST.get('discussions', None) == 'on'
    feature_flags.cohort_map = request.POST.get('cohort_map', None) == 'on'
    feature_flags.proficiency = request.POST.get('proficiency', None) == 'on'
    feature_flags.learner_dashboard = request.POST.get('learner_dashboard', None) == 'on'
    feature_flags.progress_page = request.POST.get('progress_page', None) == 'on'
    feature_flags.notifications = request.POST.get('notifications', None) == 'on'
    feature_flags.branding = request.POST.get('branding', None) == 'on'
    feature_flags.resources = request.POST.get('resources', None) == 'on'
    feature_flags.save()

    return HttpResponse(
        json.dumps(feature_flags.as_json()),
        content_type="application/json"
    )

def course_learner_dashboard_bookmark_tile(request, learner_dashboard_id):

    if 'tile_id' in request.POST:
        try:
            tile = LearnerDashboardTile.objects.get(id=int(request.POST['tile_id']))
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        try:
            bookmark = TileBookmark.objects.get(user=request.user.id)
            bookmark.tile = tile
            bookmark.lesson_link = None
            bookmark.save()

        except:
            bookmark = TileBookmark(
                user = request.user.id,
                tile=tile,
                learner_dashboard_id=learner_dashboard_id,
            )
            bookmark.save()

        return HttpResponse(status=200)

def course_learner_dashboard_bookmark_lesson(request, learner_dashboard_id):

    if 'lesson_link' in request.POST and 'tile_id' in request.POST:

        if request.POST['tile_id']:
            try:
                bookmark = TileBookmark.objects.get(user=request.user.id)
                if int(request.POST['tile_id']) == bookmark.tile.id:
                    bookmark.lesson_link = request.POST['lesson_link']
                    bookmark.save()
            except ObjectDoesNotExist:
                return HttpResponse(status=404)

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=204)

@login_required
def course_learner_dashboard_calendar(request, learner_dashboard_id):

    try:
        learner_dashboard = LearnerDashboard.objects.get(pk=learner_dashboard_id)
    except:
        learner_dashboard = None

    if learner_dashboard:
        trackedData = LearnerDashboardTile.objects.filter(
            learner_dashboard=learner_dashboard,
            show_in_calendar = True
        ).exclude(tile_type='1').exclude(tile_type='6').exclude(tile_type='7')

        notTrackedData = LearnerDashboardTile.objects.filter(
            learner_dashboard=learner_dashboard,
            show_in_calendar = True
        ).exclude(tile_type='2').exclude(tile_type='3').exclude(tile_type='4').exclude(tile_type='5')
    else:
        return HttpResponse(status=404)


    first = datetime.now().replace(day=1)
    now = datetime(first.year, first.month, first.day)

    dates = [
        add_months_to_date(now, -1).replace(day=1).strftime("%Y-%m-%d"),
        now.strftime("%Y-%m-%d"),
        add_months_to_date(now, 1).replace(day=1).strftime("%Y-%m-%d"),
        add_months_to_date(now, 2).replace(day=1).strftime("%Y-%m-%d"),
        add_months_to_date(now, 3).replace(day=1).strftime("%Y-%m-%d")
    ]

    tile_ids = [str(i.id) for i in trackedData]

    progressData = LearnerDashboardTileProgress.objects.filter(user=request.user.id, milestone_id__in=tile_ids)

    if len(trackedData) > len(progressData):
        createProgressObjects(progressData, tile_ids, request.user.id)
        progressData = LearnerDashboardTileProgress.objects.filter(
            user=request.user.id,
            milestone_id__in=tile_ids
        )

    enum = 0
    milestoneDataJson = {}
    for i, content in enumerate(progressData):
        milestoneDataJson[i] = {
            "name": content.milestone.title,
            "label": content.milestone.label,
            "link": content.milestone.link,
            "start": int(content.milestone.start_date.strftime("%s")) * 1000,
            "end": int(content.milestone.end_date.strftime("%s")) * 1000,
            "row": int(content.milestone.row),
            "note": content.milestone.note,
            "tile_type": content.milestone.tile_type,
            "user_progress": content.percentage,
            "cohort_progress": 0,
            "fa_icon": content.milestone.fa_icon,
            "publish_date": None if content.milestone.publish_date is None else int(content.milestone.publish_date.strftime("%s")) * 1000,
            "track_progress": content.milestone.track_progress,
        }

        if check_tile_type(content):
            milestoneDataJson[i]["link"] = content.milestone.link + str(content.milestone.id) + "/" + str(learner_dashboard_id)

        enum = i

    for i, content in enumerate(notTrackedData):
        milestoneDataJson[i + enum + 1] = {
            "name": content.title,
            "label": content.label,
            "link": content.link,
            "start": int(content.start_date.strftime("%s")) * 1000,
            "end": int(content.end_date.strftime("%s")) * 1000,
            "row": int(content.row),
            "note": content.note,
            "tile_type": content.tile_type,
            "fa_icon": content.fa_icon,
            "publish_date": None if content.publish_date is None else int(content.publish_date.strftime("%s")) * 1000,
            "track_progress": content.track_progress,
        }

    data ={
        'dates': dates,
        'milestones': json.dumps(milestoneDataJson),
    }

    if request.is_ajax():
        html = loader.render_to_string('courses/course_learner_dashboard_calendar.haml', data, context_instance=RequestContext(request))

        return HttpResponse(json.dumps({'html': html}), content_type="application/json")
    else:
        return HttpResponse(status=404)
 
def check_tile_type(element):

    if element.milestone.tile_type == "2" or element.milestone.tile_type == "3" or element.milestone.tile_type == "5":
        return True
    else:
        return False

@login_required
def get_user_progress_json(request, course_id):
    user_progress = course_api.get_course_metrics_completions(course_id=course_id, user_id = request.user.id, skipleaders = True)
    if user_progress:
        data = {"user_progress": user_progress.completions}
    else:
       data = {"user_progress": 0}

    return HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )

@login_required
def get_user_gradebook_json(request, course_id):
    proficiency = course_api.get_course_metrics_grades(course_id, user_id=request.user.id, grade_object_type=Proficiency)
    if proficiency:
        data = {"proficiency": {"user_grade_value": proficiency.user_grade_value }}
    else:
       data = {"proficiency": None}

    return HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )

@login_required
def get_user_completion_json(request, course_id):
    grades = {grade.course_id: grade for grade in user_api.get_user_grades(request.user.id)}
    course_grade = grades.get(course_id, None)
    if course_grade:
        data = {"grades": {"course_id":course_grade.course_id, "current_grade":course_grade.current_grade,
        "proforma_grade":course_grade.proforma_grade, "complete_status":course_grade.complete_status}}
    else:
       data = {"grades": None}

    return HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )

@login_required
def get_user_complete_gradebook_json(request, course_id):
    user_grades = user_api.get_user_full_gradebook(user_id = request.user.id, course_id=course_id)
    if user_grades:
        data = {"user_gradebook": user_grades}
    else:
       data = {"user_gradebook": None}
    
    return HttpResponse(
        json.dumps(data),
        content_type='application/json'
    )
