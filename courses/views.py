''' rendering templates from requests related to courses '''
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from admin.controller import load_course
from admin.models import WorkGroup
from api_client import course_api, user_api, workgroup_api
from api_client.api_error import ApiError
from api_client.group_api import PERMISSION_GROUPS
from lib.authorization import permission_group_required
from lib.util import DottableDict
from main.models import CuratedContentItem

from .controller import inject_gradebook_info, round_to_int, Proficiency
from .controller import build_page_info_for_course, locate_chapter_page, load_static_tabs, load_lesson_estimated_time
from .controller import update_bookmark, progress_percent, group_project_reviews
from .controller import get_progress_leaders, get_proficiency_leaders, get_social_metrics, average_progress, choose_random_ta
from .controller import get_group_project_for_user_course, get_group_project_for_workgroup_course, group_project_location
from .user_courses import check_user_course_access, standard_data, load_course_progress, check_company_admin_user_access
from .user_courses import get_current_course_for_user, set_current_course_for_user, get_current_program_for_user

# Temporary id converter to fix up problems post opaque keys
from lib.util import LegacyIdConvert

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
    static_tabs = load_static_tabs(course_id)
    course = standard_data(request).get("course", None)
    proficiency = course_api.get_course_metrics_grades(course_id, user_id=request.user.id, grade_object_type=Proficiency)
    load_lesson_estimated_time(course)
    social = get_social_metrics(course_id, request.user.id)

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
    }
    return render(request, 'courses/course_main.haml', data)

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
    static_tabs = load_static_tabs(course_id)
    data = {
        "syllabus": static_tabs.get("syllabus", None)
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
        ta_user_json = ta_user.to_json()
    ta_user_id = ta_user.id if ta_user else None

    if len(organizations) > 0:
        organization = organizations[0]
        organizationUsers = course_api.get_users_list_in_organizations(course_id, organizations = organization.id)
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
                    metrics.groups_users.append(user.to_dict())
    metrics.groups_users = json.dumps(metrics.groups_users)

    metrics.cities = []
    cities = course_api.get_course_metrics_by_city(course_id)
    for city in cities:
        if city.city != '':
            metrics.cities.append({'city': city.city, 'count': city.count})
    metrics.cities = json.dumps(metrics.cities)

    data = {
        'proficiency': proficiency,
        'completions': completions,
        'social': social,
        'metrics': metrics,
        'ta_user': ta_user_json,
        'ta_email': settings.TA_EMAIL_GROUP,
        'leaderboard_ranks': [1,2,3],
    }
    return render(request, 'courses/course_cohort.haml', data)

def _render_group_work(request, course, project_group, group_project):

    seqid = request.GET.get("seqid", None)
    if seqid and " " in seqid:
        seqid = seqid.replace(" ", "+")

    if not group_project is None:
        sequential, page = group_project_location(
            group_project,
            seqid
        )
        vertical_usage_id = page.vertical_usage_id() if page else None
    else:
        sequential = page = vertical_usage_id = None

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN

    ta_user = choose_random_ta(course.id)

    data = {
        "lesson_content_parent_id": "course-group-work",
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "course_id": course.id,
        "legacy_course_id": LegacyIdConvert.legacy_from_new(course.id),
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "project_group": project_group,
        "group_project": group_project,
        "current_sequential": sequential,
        "current_page": page,
        "ta_user": ta_user,
        "group_work_url": request.path_info,
    }
    return render(request, 'courses/course_group_work.haml', data)

@login_required
@check_user_course_access
def user_course_group_work(request, course_id):

    # remove this in case we are a TA who is taking a course themselves
    user_api.delete_user_preference(request.user.id, "TA_REVIEW_WORKGROUP")

    course = load_course(course_id, request=request)
    project_group, group_project = get_group_project_for_user_course(request.user.id, course)
    set_current_course_for_user(request, course_id)

    return _render_group_work(request, course, project_group, group_project)

@login_required
@permission_group_required(PERMISSION_GROUPS.MCKA_TA)
def workgroup_course_group_work(request, course_id, workgroup_id):

    # set this workgroup as the preference for reviewing
    user_api.set_user_preferences(request.user.id, {"TA_REVIEW_WORKGROUP": workgroup_id})

    course = load_course(course_id, request=request)
    project_group, group_project = get_group_project_for_workgroup_course(workgroup_id, course)

    return _render_group_work(request, course, project_group, group_project)

@login_required
@check_user_course_access
def course_discussion(request, course_id):

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

    mcka_ta = choose_random_ta(course_id)

    data = {
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "has_course_discussion": has_course_discussion,
        "course_id": course_id,
        "legacy_course_id": LegacyIdConvert.legacy_from_new(course_id),
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "mcka_ta": mcka_ta
    }
    return render(request, 'courses/course_discussion.haml', data)

@login_required
def course_discussion_userprofile(request, course_id, user_id):

    data = {
        "course_id": course_id,
    }
    return render(request, 'courses/course_discussion_userprofile.haml', data)

def _course_progress_for_user(request, course_id, user_id):

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

@login_required
@check_company_admin_user_access
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def course_user_progress(request, user_id, course_id):
    return _course_progress_for_user(request, course_id, user_id)

@login_required
@check_user_course_access
def course_progress(request, course_id):
    return _course_progress_for_user(request, course_id, request.user.id)

@login_required
@check_user_course_access
def course_resources(request, course_id):
    static_tabs = load_static_tabs(course_id)
    data = {
        "resources": static_tabs.get("resources", None)
    }
    return render(request, 'courses/course_resources.haml', data)

@login_required
@check_user_course_access
def navigate_to_lesson_module(request, course_id, chapter_id, page_id):

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
        "legacy_course_id": LegacyIdConvert.legacy_from_new(course_id),
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

    data.update({
        "remote_session_key": remote_session_key,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
    })
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

def infer_course_navigation(request, course_id):
    ''' handler to call infer chapter nav with no chapter '''
    return infer_chapter_navigation(request, course_id, None)

def infer_default_navigation(request):
    ''' handler to call infer chapter nav with no course '''
    return infer_chapter_navigation(request, None, None)

@login_required
@check_user_course_access
def contact_ta(request, course_id):
    user = user_api.get_user(request.user.id)
    email_header_from = user.email
    email_from = "{}<{}>".format(
        user.formatted_name,
        settings.APROS_EMAIL_SENDER
    )
    email_to = settings.TA_EMAIL_GROUP
    email_content = request.POST["ta_message"]
    course = course_api.get_course(course_id)
    email_subject = "Ask a TA - {}".format(course.name)
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
    course = course_api.get_course(course_id)
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
    course = course_api.get_course(course_id)
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

