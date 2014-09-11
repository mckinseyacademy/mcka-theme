''' Core logic to sanitise information for views '''
#from urllib import quote_plus, unquote_plus

import copy
import random

from django.conf import settings

from accounts.middleware.thread_local import set_static_tab_context, get_static_tab_context

from api_client import course_api, user_api, user_models, workgroup_api
from api_client.project_models import Project
from api_client.group_api import get_groups_of_type, PERMISSION_GROUPS
from api_client.group_models import GroupInfo
from api_client.gradebook_models import CourseSummary, GradeSummary
from api_client.json_object import JsonObject
from admin.models import WorkGroup
from admin.controller import load_course, get_group_activity_xblock, is_group_activity, get_group_project_activities

# warnings associated with members generated from json response
# pylint: disable=maybe-no-member

# logic functions - recieve api implementor for test

class AcademyGradeAssessmentType(JsonObject):
    @property
    def type_name(self):
        return self.type[len(settings.GROUP_PROJECT_IDENTIFIER):] if self.is_group_assessment else self.type;

    @property
    def is_group_assessment(self):
        return self.type.startswith(settings.GROUP_PROJECT_IDENTIFIER)

class AcademyGradePolicy(JsonObject):
    object_map = {
        "GRADER": AcademyGradeAssessmentType,
    }

class AcademyGradebook(JsonObject):
    object_map = {
        "courseware_summary": CourseSummary,
        "grade_summary": GradeSummary,
        "grading_policy": AcademyGradePolicy,
    }

def build_page_info_for_course(
    request,
    course_id,
    lesson_id,
    module_id,
    course_api_impl=course_api
):
    '''
    Returns course structure and user's status within course
        course_api_impl - optional api client module to use (useful in mocks)
    '''

    course = copy.deepcopy(load_course(course_id, 4, course_api_impl, request=request))

    # something sensible if we fail...
    if len(course.chapters) < 1:
        return course

    # Set default current lesson just in case
    course.current_lesson = course.chapters[0]

    previous_module = None
    next_module = None

    # Inject lesson information for course
    for idx, lesson in enumerate(course.chapters, start=1):
        lesson.index = idx
        lesson.navigation_url = '/courses/{}/lessons/{}'.format(course_id, lesson.id)
        lesson.module_count = 0
        lesson.modules = []

        # Set current lesson and lesson bookmark
        if lesson.id == lesson_id:
            course.current_lesson = lesson
            lesson.bookmark = True
        else:
            lesson.bookmark = False

        # Inject full module list for lesson
        for sequential in lesson.sequentials:
            lesson.module_count += len(sequential.pages)
            lesson.modules.extend(sequential.pages)

        # Inject module data for navigation
        for idx, module in enumerate(lesson.modules, start=1):
            module.index = idx
            module.lesson_index = lesson.index
            module.lesson_count = lesson.module_count
            module.navigation_url = '{}/module/{}'.format(lesson.navigation_url, module.id)

            if hasattr(course, 'current_module') and next_module is None:
                next_module = module
                course.current_lesson.next_module = module

            if module_id == module.id:
                # Set the vertical id for js usage
                # method not available running tests
                if hasattr(module, 'vertical_usage_id'):
                    module.vertical_id = module.vertical_usage_id()

                # Set current lesson previous module
                course.current_lesson.previous_module = previous_module
                course.current_module = module
                module.is_current = True

            # Set previous url for use in the next module
            previous_module = module

    return course

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
    request,
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
    course = load_course(course_id, 4, course_api_impl, request=request)
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

def get_group_project_for_user_course(user_id, course):
    '''
    Returns correct group and project information for the user for this course
    '''
    # Find the user_group(s) with which this user is associated
    user_workgroups = user_api.get_user_workgroups(user_id, course.id)
    if len(user_workgroups) < 1:
        return None, None

    project_group = user_workgroups[0]
    user_ids = [str(user.id) for user in workgroup_api.get_workgroup_users(project_group.id)]
    additional_fields = ["title", "first_name", "last_name", "avatar_url"]
    project_group.members = user_api.get_users(ids=user_ids,fields=additional_fields)

    the_user_project = Project.fetch_from_url(project_group.project)
    group_project = [ch for ch in course.group_project_chapters if ch.id == the_user_project.content_id][0]

    return project_group, group_project

def get_group_project_for_workgroup_course(workgroup_id, course):
    '''
    Returns group and project information for the supplied workgroup
    '''
    workgroup = WorkGroup.fetch(workgroup_id)
    user_ids = [str(user.id) for user in workgroup.users]
    additional_fields = ["title", "first_name", "last_name", "avatar_url"]
    workgroup.members = user_api.get_users(ids=user_ids,fields=additional_fields)
    project = Project.fetch(workgroup.project)
    group_project = [ch for ch in course.group_project_chapters if ch.id == project.content_id][0]

    return workgroup, group_project

def group_project_location(group_project, sequential_id=None):
    '''
    Returns current sequential_id and page_id for the user for their group project
    '''
    sequential = group_project.sequentials[0]
    for seq in group_project.sequentials:
        # is it the chosen one
        if seq.id == sequential_id:
            sequential = seq

        # Is it a group_project xblock
        seq.is_group_activity = is_group_activity(sequential)

    page = sequential.pages[0] if len(sequential.pages) > 0 else None

    return sequential, page

def load_static_tabs(course_id):
    static_tabs = get_static_tab_context()
    if static_tabs is None:
        static_tabs = course_api.get_course_tabs(course_id)
        set_static_tab_context(static_tabs)

    return static_tabs

def round_to_int(value):
    return int(round(value))

def average_progress(course, user_id):
    metrics = course_api.get_course_metrics_completions(course.id, user_id)
    return metrics.course_avg

def progress_percent(completion_count, module_count):
    if module_count > 0:
        return round_to_int(100*completion_count/module_count)
    else:
        return 0

def group_project_reviews(user_id, course_id, project_workgroup, project_chapter):
    '''
    Returns group work reviews & average score for a project
    '''
    def mean(array_values):
        return sum(array_values)/float(len(array_values)) if len(array_values) > 0 else None

    review_items = WorkGroup.get_workgroup_review_items(project_workgroup.id)

    # distinct reviewers
    reviewer_ids = set([item.reviewer for item in review_items])

    # find group activities in this project

    group_activities = get_group_project_activities(project_chapter)
    for activity in group_activities:
        group_project_xblock = get_group_activity_xblock(activity)
        activity_reviews = [item for item in review_items if group_project_xblock.id == item.content_id]

        # average by reviewer
        activity.grades = []
        for reviewer_id in reviewer_ids:
            grades = [int(review.answer) for review in activity_reviews if reviewer_id == review.reviewer and is_number(review.answer)]
            activity.grades.append(mean(grades))

        # average score for this activity
        activity.score = mean(filter(None, activity.grades))

    group_work_avg = mean([a.score for a in group_activities if not a.score is None])
    return group_activities, group_work_avg

def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    return True

def get_proficiency_leaders(course_id, user_id):
    proficiency = course_api.get_course_metrics_grades(course_id, user_id)
    proficiency.user_grade_display = round_to_int(100*proficiency.user_grade)
    proficiency.course_avg_display = round_to_int(100*proficiency.course_avg) if proficiency.course_avg else 0
    tailor_leader_list(proficiency.leaders)
    return proficiency

def get_progress_leaders(course_id, user_id):
    completions = course_api.get_course_metrics_completions(course_id, user_id)
    tailor_leader_list(completions.leaders)
    return completions

def tailor_leader_list(leaders):
    for rank, leader in enumerate(leaders, 1):
        leader.rank = rank
        if hasattr(leader, 'points_scored'):
            leader.points_scored = round_to_int(leader.points_scored)
        if leader.avatar_url is None:
            leader.avatar_url = user_models.UserResponse.default_image_url()

def social_total(social_metrics):
    social_total = 0

    for key, val in settings.SOCIAL_METRIC_POINTS.iteritems():
        social_total += getattr(social_metrics, key, 0) * val

    return social_total

def get_social_metrics(course_id, user_id):
    ''' returns social engagement points and leaders '''
    course_metrics = course_api.get_course_social_metrics(course_id)
    total_enrollments = course_metrics.total_enrollments
    users = []
    point_sum = 0

    # calculate total social score for each user in course
    user_ids = [u_id for u_id, user_metrics in course_metrics.users.__dict__.iteritems()]
    additional_fields = ["avatar_url","title"]
    user_dict = {str(user.id): user for user in user_api.get_users(ids=user_ids,fields=additional_fields)} if len(user_ids) > 0 else {}

    for u_id, user_metrics in course_metrics.users.__dict__.iteritems():
        user = user_dict[u_id]
        user.points = social_total(user_metrics)
        user.avatar_url = user.image_url(40)
        point_sum += user.points
        users.append(user)

    course_avg = point_sum / total_enrollments if total_enrollments > 0 else 0

    # sort by social score
    leaders = sorted(users, key=lambda u: u.points, reverse=True)

    # assign rank
    for rank, leader in enumerate(leaders, 1):
        leader.rank = rank

    user = next((l for l in leaders if int(l.id) == int(user_id)), None)

    return {
        'points': user.points if user else 0,
        'position': user.rank if user else None,
        'course_avg': round_to_int(course_avg),
        'leaders': leaders[:3]
    }

def get_ta_users(course_id):
    role = "staff"
    ta_users_base = [str(user.id) for user in course_api.get_users_filtered_by_role(course_id) if user.role == role]
    additional_fields = ["title", "avatar_url", "city", "full_name"]
    ta_users = user_api.get_users(ids=ta_users_base,fields=additional_fields) if len(ta_users_base) > 0 else []
    return ta_users

def choose_random_ta(course_id):
    ta_users = [u for u in get_ta_users(course_id) if u.city]
    ta_user = None
    if len(ta_users) > 0:
        ta_user = random.choice(ta_users)
    return ta_user

def load_lesson_estimated_time(course):
    static_tabs = load_static_tabs(course.id)
    estimated_time = static_tabs.get("estimated time", None)

    if estimated_time:
        estimates = [s.strip() for s in estimated_time.content.splitlines()]
        for idx, lesson in enumerate(course.chapters):
            if idx < len(estimates):
                lesson.estimated_time = estimates[idx]

    return course

def inject_gradebook_info(user_id, course):
    # Inject lesson assessment scores
    assesments = {}
    gradebook = user_api.get_user_gradebook(user_id, course.id, AcademyGradebook)
    if gradebook.courseware_summary:
        for lesson in gradebook.courseware_summary:
            percent = None
            for section in lesson.sections:
                if section.graded == True:
                    points = section.section_total[0]
                    max_points = section.section_total[1]
                    if max_points > 0:
                        percent = round_to_int(100*points/max_points)
                    else:
                        percent = 0
                    assesments[section.url_name] = percent

    for lesson in course.chapters:
        lesson.assesment_score = None
        for sequential in lesson.sequentials:
            url_name = sequential.id.split('+')[-1]
            if url_name in assesments:
                lesson.assesment_score = assesments[url_name]
                break

    return gradebook

