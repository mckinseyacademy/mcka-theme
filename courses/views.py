''' rendering templates from requests related to courses '''
import math
import json
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.template.defaultfilters import floatformat
from main.models import CuratedContentItem

from .controller import build_page_info_for_course, locate_chapter_page, load_static_tabs
from .controller import update_bookmark, group_project_location, progress_percent, group_project_reviews, get_course_ta
from .controller import build_progress_leader_list, build_proficiency_leader_list, social_metrics, average_progress
from lib.authorization import is_user_in_permission_group
from api_client.group_api import PERMISSION_GROUPS
from api_client import course_api, user_api, project_api, user_models, workgroup_api
from admin.controller import load_course
from admin.models import WorkGroup
from accounts.controller import get_current_course_for_user, set_current_course_for_user, get_current_program_for_user
from accounts.controller import check_user_course_access

# Create your views here.

def _inject_formatted_data(program, course, page_id, static_tab_info=None):
    if program:
        for program_course in program.courses:
            program_course.course_class = ""
            if program_course.id == course.id:
                program_course.course_class = "current"

    found_current_page = False

    for idx, lesson in enumerate(course.chapters, start=1):
        lesson.index = idx
        if static_tab_info:
            lesson_description = static_tab_info.get("lesson{}".format(idx), None)
            if lesson_description:
                lesson.description = lesson_description.content
        if page_id:
            for sequential in lesson.sequentials:
                for page in sequential.pages:
                    page.status_class = "complete"
                    is_current = page_id == page.id
                    if is_current:
                        page.status_class = "current"
                        found_current_page = True
                    elif found_current_page:
                        page.status_class = "incomplete"

@login_required
@check_user_course_access
def course_landing_page(request, course_id):
    '''
    Course landing page for user for specified course
    etc. from user settings
    '''

    course = load_course(course_id, 3)
    load_static_tabs(course_id)
    set_current_course_for_user(request, course_id)

    social_metrics = user_api.get_course_social_metrics(request.user.id, course_id)
    proficiency = course_api.get_course_metrics_proficiency(course_id, request.user.id)

    social_total = 0
    try:
        social_metrics = user_api.get_course_social_metrics(request.user.id, course_id)
        for key, val in settings.SOCIAL_METRIC_POINTS.iteritems():
            social_total += getattr(social_metrics, key) * val
    except:
        social_total = 0

    data = {
        "user": request.user,
        "articles": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.ARTICLE).order_by('sequence')[:3],
        "videos": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.VIDEO).order_by('sequence')[:3],
        "tweet": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.TWEET).order_by('sequence').last(),
        "quote": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.QUOTE).order_by('sequence').last(),
        "infographic": CuratedContentItem.objects.filter(course_id=course_id, content_type=CuratedContentItem.IMAGE).order_by('sequence').last(),
        "proficiency": int(round(proficiency.points)),
        "proficiency_graph": int(5 * round(proficiency.points/5)),
        "cohort_proficiency_average": int(round(proficiency.course_avg)),
        "social_total": social_total,
        "cohort_social_average": 28,
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
    data = {
        "news": course_api.get_course_news(course_id)
    }
    return render(request, 'courses/course_news.haml', data)

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))

@login_required
@check_user_course_access
def course_cohort(request, course_id):
    course = load_course(course_id)

    proficiency = course_api.get_course_metrics_proficiency(course_id, request.user.id)
    proficiency.leaders = build_proficiency_leader_list(proficiency.leaders)
    proficiency.points = floatformat(proficiency.points)
    proficiency.course_avg = floatformat(proficiency.course_avg)

    completions = course_api.get_course_metrics_completions(course_id, request.user.id)
    module_count = course.module_count()
    completions.leaders = build_progress_leader_list(completions.leaders, module_count)
    completions.completion_percent = progress_percent(completions.completions, module_count)
    completions.course_avg_percent = progress_percent(completions.course_avg, module_count)

    social = social_metrics(course_id, request.user.id)

    metrics = course_api.get_course_metrics(course_id)
    workgroups = user_api.get_user_workgroups(request.user.id, course_id)
    organizations = user_api.get_user_organizations(request.user.id)
    if len(organizations) > 0:
        organization = organizations[0]
        organizationUsers = course_api.get_users_list_in_organizations(course_id, organizations = organization.id)
        metrics.company_enrolled = len(organizationUsers)
    metrics.groups_users = []
    if len(workgroups) > 0:
        workgroup = workgroup_api.get_workgroup(workgroups[0].id)
        metrics.group_enrolled = len(workgroup.users)
        if workgroup.users > 0:
            for student in workgroup.users:
                user = user_api.get_user(student.id)
                if user.get('city') != '':
                    metrics.groups_users.append({"id": user.get('id'),
                                                    "username": user.get('username'),
                                                    "first_name": user.get('first_name'),
                                                    "last_name": user.get('last_name'),
                                                    "country": user.get('country'),
                                                    "city": user.get('city'),
                                                    "avatar_url": user.image_url(size=40),
                                                    "full_name": user.get('full_name'),
                                                    "title": user.get('title'),
                                                })
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
    }
    return render(request, 'courses/course_cohort.haml', data)

@login_required
@check_user_course_access
def course_group_work(request, course_id):

    seq_id = request.GET.get("seqid", None)
    project_group, group_project, sequential, page = group_project_location(
        request.user.id,
        load_course(course_id, 4),
        seq_id
    )
    vertical_usage_id = page.vertical_usage_id() if page else None

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN

    # Get course info
    set_current_course_for_user(request, course_id)

    data = {
        "lesson_content_parent_id": "course-group-work",
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "course_id": course_id,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "project_group": project_group,
        "group_project": group_project,
        "current_sequential": sequential,
        "current_page": page,
    }
    return render(request, 'courses/course_group_work.haml', data)

@login_required
@check_user_course_access
def course_discussion(request, course_id):

    course = load_course(course_id)
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

    mcka_ta = get_course_ta()

    data = {
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "has_course_discussion": has_course_discussion,
        "course_id": course_id,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "mcka_ta": mcka_ta
    }
    return render(request, 'courses/course_discussion.haml', data)

@login_required
@check_user_course_access
def course_progress(request, course_id):

    course = load_course(course_id, 3)
    gradebook = user_api.get_user_gradebook(request.user.id, course_id)

    graders = gradebook.grading_policy.GRADER
    for grader in graders:
        grader.weight = floatformat(grader.weight*100)

    pass_grade = floatformat(gradebook.grading_policy.GRADE_CUTOFFS.Pass*100)

    if course.group_project_chapters:
        project_chapter = course.group_project_chapters[0]
        group_activities, group_work_avg = group_project_reviews(request.user.id, course_id, project_chapter)
    else:
        group_activities = []
        group_work_avg = 0

    # format scores & grades
    for activity in group_activities:
        if activity.score is not None:
            activity.score = floatformat(round(activity.score))
        for i, grade in enumerate(activity.grades):
            if grade is not None:
                activity.grades[i] = floatformat(round(grade))

    bar_chart = [{'pass_grade': pass_grade, 'key': 'Lesson Scores', 'values': []}]
    for grade in gradebook.grade_summary.section_breakdown:
        bar_chart[0]['values'].append({
           'label': grade.label,
           'value': grade.percent*100,
           'color': '#b1c2cc'
        })

    bar_chart[0]['values'].append({
        'label': 'GROUP WORK\n AVG.',
        'value': group_work_avg,
        'color': '#66a5b5'
    })

    total = gradebook.grade_summary.percent*100
    bar_chart[0]['values'].append({
        'label': 'TOTAL',
        'value': total,
        'color': '#e37121'
    })

    data = {
        'bar_chart': json.dumps(bar_chart),
        'pass_grade': pass_grade,
        'graders': graders,
        'group_activities': group_activities,
        "average_progress": average_progress(course, request.user.id),
    }
    return render(request, 'courses/course_progress.haml', data)

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
    # Get course info
    course, current_chapter, current_sequential, current_page = build_page_info_for_course(
        course_id, chapter_id, page_id)

    # Take note that the user has gone here
    set_current_course_for_user(request, course_id)
    update_bookmark(
        request.user.id,
        course_id,
        chapter_id,
        current_sequential.id,
        page_id
    )

    # Load the current program for this user
    program = get_current_program_for_user(request)

    # Inject formatted data for view
    _inject_formatted_data(program, course, page_id)

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN

    vertical_usage_id = current_page.vertical_usage_id()

    data = {
        "user": request.user,
        "course": course,
        "current_chapter": current_chapter,
        "current_sequential": current_sequential,
        "current_page": current_page,
        "program": program,
        "lesson_content_parent_id": "course-lessons",
        "course_id": course_id,
        "vertical_usage_id": vertical_usage_id,
        "remote_session_key": remote_session_key,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
    }
    return render(request, 'courses/course_lessons.haml', data)

def course_notready(request, course_id):
    return render(request, 'courses/course_notready.haml')

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
    email_header_from = request.user.email
    email_from = settings.APROS_EMAIL_SENDER
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
    email_from = settings.APROS_EMAIL_SENDER
    email_header_from = request.user.email
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
def contact_member(request, course_id):
    email_from = settings.APROS_EMAIL_SENDER
    email_header_from = request.user.email
    email_to = request.POST["member-email"]
    email_content = request.POST["member_message"]
    course = course_api.get_course(course_id)
    email_subject = "Group Project Message - {}".format(course.name) #just for testing
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
