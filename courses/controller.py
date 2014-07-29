''' Core logic to sanitise information for views '''
#from urllib import quote_plus, unquote_plus

import datetime
from django.template.defaultfilters import floatformat

from django.conf import settings

from accounts.middleware.thread_local import set_static_tab_context, get_static_tab_context

from api_client import course_api, user_api, user_models, workgroup_api
from api_client.api_error import ApiError
from api_client.project_models import Project
from api_client.group_api import get_groups_of_type, PERMISSION_GROUPS
from api_client.group_models import GroupInfo
from admin.models import WorkGroup
from admin.controller import load_course

GROUP_PROJECT_CATEGORY = 'group-project'

# warnings associated with members generated from json response
# pylint: disable=maybe-no-member

# logic functions - recieve api implementor for test

def build_page_info_for_course(
    course_id,
    chapter_id,
    page_id,
    course_api_impl=course_api
):
    '''
    Returns course structure and user's status within course
        course_api_impl - optional api client module to use (useful in mocks)
    '''
    course = load_course(course_id, 4, course_api_impl)

    # something sensible if we fail...
    if len(course.chapters) < 1:
        return course, None, None, None

    current_chapter = course.chapters[0]
    current_sequential = None
    current_page = None

    prev_page = None

    for chapter in course.chapters:
        chapter.navigation_url = '/courses/{}/lessons/{}'.format(course_id, chapter.id)
        if chapter.id == chapter_id:
            current_chapter = chapter
            chapter.bookmark = True

        for sequential in chapter.sequentials:
            for page in sequential.pages:
                page.prev_url = None
                page.next_url = None
                page.navigation_url = '{}/module/{}'.format(chapter.navigation_url, page.id)

                if page.id == page_id:
                    current_page = page
                    current_sequential = sequential

                if prev_page is not None:
                    page.prev_url = prev_page.navigation_url
                    prev_page.next_url = page.navigation_url
                prev_page = page

    if not current_page:
        current_sequential = current_chapter.sequentials[0] if len(current_chapter.sequentials) > 0 else None
        current_page = current_sequential.pages[0] if current_sequential and len(current_sequential.pages) > 0 else None

    if len(current_sequential.pages) > 0:
        if current_sequential == current_chapter.sequentials[-1] and current_page == current_sequential.pages[-1] and current_chapter != course.chapters[-1]:
            current_page.next_lesson_link = True

    return course, current_chapter, current_sequential, current_page

def get_course_position_tree(user_id, course_id, user_api_impl=user_api):
    course_detail = False
    try:
        course_detail = user_api_impl.get_user_course_detail(user_id, course_id)
    except:
        course_detail = False

    if course_detail == False or not hasattr(course_detail, 'position_tree'):
        return None

    return course_detail.position_tree

def locate_chapter_page(
    user_id,
    course_id,
    chapter_id,
    user_api_impl=user_api,
    course_api_impl=course_api
):
    '''
    Returns current chapter and page for given course from user's status
    Chapter defaults to bookmark if not provided, to 1st chapter if no bookmark
    Page defaults to bookmark if not provided, to 1st page if no bookmark
        course_api_impl - optional api client module to use (useful in mocks)
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    course = load_course(course_id, 4, course_api_impl)
    chapter = None
    page = None

    position_tree = get_course_position_tree(user_id, course_id, user_api_impl)
    if chapter_id is None:
        chapter_id = position_tree.chapter.id if position_tree else None
    chapter_candidates = [c for c in course.chapters if c.id == chapter_id]
    if len(chapter_candidates) > 0:
        chapter = chapter_candidates[0]

    if chapter is None and len(course.chapters) > 0:
        chapter = course.chapters[0]

    if chapter and chapter.sequentials:
        last_sequential_id = position_tree.sequential.id if position_tree else None
        sequential_candidates = [s for s in chapter.sequentials if s.id == last_sequential_id]
        if len(sequential_candidates) > 0 and sequential_candidates[0].pages:
            last_page_id = position_tree.vertical.id if position_tree else None
            page_candidates = [p for p in sequential_candidates[0].pages if p.id == last_page_id]
            if len(page_candidates) > 0:
                page = page_candidates[0]
            elif len(sequential_candidates[0].pages) > 0:
                page = sequential_candidates[0].pages[0]
        elif len(chapter.sequentials) > 0 and chapter.sequentials[0].pages and len(chapter.sequentials[0].pages) > 0:
            page = chapter.sequentials[0].pages[0]

    chapter_id = chapter.id if chapter else None
    page_id = page.id if page else None

    return course_id, chapter_id, page_id

# pylint: disable=too-many-arguments
def update_bookmark(user_id, course_id, chapter_id, sequential_id, page_id, user_api_impl=user_api):
    '''
    Informs the openedx api of user's location
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    user_api_impl.set_user_bookmark(
        user_id,
        course_id,
        chapter_id,
        sequential_id,
        page_id
    )

def group_project_location(user_id, course, sequential_id=None):
    '''
    Returns current sequential_id and page_id for the user for their group project
    '''
    # Find the user_group(s) with which this user is associated
    user_workgroups = user_api.get_user_workgroups(user_id)
    user_projects = [Project.fetch_from_url(wg.project) for wg in user_workgroups]

    # So, we can find the project for the user
    user_course_projects = [cp for cp in user_projects if cp.course_id == course.id]
    if len(user_course_projects) < 1:
        return None, None, None, None

    the_user_project = user_course_projects[0]

    group_project = [ch for ch in course.group_project_chapters if ch.id == the_user_project.content_id][0]

    user_course_workgroups = [wg for wg in user_workgroups if wg.id in the_user_project.workgroups]
    if len(user_course_workgroups) < 1:
        return None, group_project, None, None

    project_group = user_course_workgroups[0]
    project_group.members = [user_api.get_user(user.id) for user in workgroup_api.get_workgroup_users(project_group.id)]

    # Get the right location within this group project - can't do this yet
    #course_detail = get_course_position_tree(user_id, course.id)

    sequential = group_project.sequentials[0]
    for seq in group_project.sequentials:
        # is it the chosen one
        if seq.id == sequential_id:
            sequential = seq

        # Is it a group_project xblock
        seq.is_group_project = len(sequential.pages) > 0 and "group-project" in sequential.pages[0].child_category_list()

    page = sequential.pages[0] if len(sequential.pages) > 0 else None

    return project_group, group_project, sequential, page

def load_static_tabs(course_id):
    static_tabs = get_static_tab_context()
    if static_tabs is None:
        static_tabs = course_api.get_course_tabs(course_id)
        set_static_tab_context(static_tabs)

    return static_tabs

def load_course_progress(course, user_id):
    completions = course_api.get_course_completions(course.id, user_id)
    completed_ids = [result.content_id for result in completions]
    component_ids = course.components_ids()
    for lesson in course.chapters:
        lesson.progress = 0
        lesson_component_ids = course.lesson_component_ids(lesson.id)
        if len(lesson_component_ids) > 0:
            matches = set(lesson_component_ids).intersection(completed_ids)
            lesson.progress = 100 * len(matches) / len(lesson_component_ids)
    actual_completions = set(component_ids).intersection(completed_ids)
    course.user_progress = 100 * len(actual_completions) / len(component_ids)

def average_progress(course, user_id):
    module_count = course.module_count()
    metrics = course_api.get_course_metrics_completions(course.id, user_id)
    return progress_percent(metrics.course_avg, module_count)

def progress_percent(completion_count, module_count):
    if module_count > 0:
        return int(round(100*completion_count/module_count))
    else:
        return 0

def group_project_reviews(user_id, course_id, project_chapter):
    '''
    Returns group work reviews & average score for a project
    '''

    # user's group for this course
    user_workgroups = user_api.get_user_workgroups(user_id, course_id)

    if not user_workgroups:
        return [], 0

    workgroup = user_workgroups[0] if user_workgroups else None
    review_items = WorkGroup.get_workgroup_review_items(workgroup.id)

    # distinct reviewers
    reviewer_ids = [item.reviewer for item in review_items]
    group_activities = []
    group_work_sum = 0

    # find group activities in this project
    for seq in project_chapter.sequentials:
        for page in seq.pages:
            if hasattr(page, 'children'):
                for child in page.children:
                    if child.category == GROUP_PROJECT_CATEGORY:
                        group_activities.append(seq)
                        break

    for activity in group_activities:
        activity.grades = []
        activity_reviews = [item for item in review_items if activity.id == item.content_id]

        # average by reviewer
        for reviewer_id in reviewer_ids:
            grades = [int(review.answer) for review in activity_reviews if reviewer_id == review.reviewer and is_number(review.answer)]
            avg = sum(grades)/float(len(grades)) if len(grades)>0 else None
            activity.grades.append(avg)
            print activity.id, reviewer_id, avg

        # average score for this activity
        activity.score = sum(filter(None, activity.grades))/float(len(activity.grades)) if len(activity.grades)>0 else None
        if activity.score:
            group_work_sum += activity.score

    group_work_avg = group_work_sum /float(len(group_activities)) if len(group_activities)>0 else 0

    return group_activities, group_work_avg

def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    return True

def get_course_ta():
    mcka_ta = None
    groups = get_groups_of_type('permission', group_object=GroupInfo)
    for group in groups:
        if group.name == PERMISSION_GROUPS.MCKA_TA:
            users = group.get_users()
            if users:
                mcka_ta = users[0]
            break
    return mcka_ta

def build_proficiency_leader_list(leaders):
    for rank, leader in enumerate(leaders, 1):
        leader.rank = rank
        leader.points_scored = floatformat(leader.points_scored)
        if leader.avatar_url is None:
            leader.avatar_url = user_models.UserResponse.default_image_url()

    return leaders

def build_progress_leader_list(leaders, module_count):
    for rank, leader in enumerate(leaders, 1):
        leader.rank = rank
        leader.completion_percent = progress_percent(leader.completions, module_count)
        if leader.avatar_url is None:
            leader.avatar_url = user_models.UserResponse.default_image_url()

    return leaders

def social_total(social_metrics):
    social_total = 0

    for key, val in settings.SOCIAL_METRIC_POINTS.iteritems():
        social_total += getattr(social_metrics, key, 0) * val

    return social_total

def social_metrics(course_id, user_id):
    ''' returns social engagement points and leaders '''
    course_metrics = course_api.get_course_social_metrics(course_id)
    users = []
    point_sum = 0

    # calculate total social score for each user in course
    for user_id, user_metrics in course_metrics.__dict__.iteritems():

        # we need username, title and avatar for each user
        user = user_api.get_user(user_id)

        user.points = social_total(user_metrics)
        user.avatar_url = user.image_url(40)
        point_sum += user.points
        users.append(user)

    course_avg = point_sum / len(users) if len(users) > 0 else 0

    # sort by social score
    leaders = sorted(users, key=lambda u: u.points, reverse=True)

    # assign rank
    for rank, leader in enumerate(leaders, 1):
        leader.rank = rank

    user = next((l for l in leaders if int(l.id) == int(user_id)), None)

    return {
        'points': user.points if user else None,
        'position': user.rank if user else None,
        'course_avg': floatformat(course_avg),
        'leaders': leaders[:3]
    }
