''' Core logic to sanitise information for views '''
# from urllib import quote_plus, unquote_plus

import copy
import logging
import random
from datetime import datetime

import re
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.translation import ugettext as _

from accounts.middleware.thread_local import (
    set_static_tab_context,
    get_static_tab_context,
    get_basic_user_data,
)
from admin.controller import load_course, is_group_activity, get_group_activity_xblock, MINIMAL_COURSE_DEPTH
from admin.models import WorkGroup, ReviewAssignmentGroup, LearnerDashboardTile, LearnerDashboardTileProgress, \
    LearnerDashboard
from api_client import course_api, user_api, workgroup_api, project_api
from api_client.api_error import ApiError
from api_client.course_api import tabs_post_process
from api_client.course_models import CourseTabs
from api_client.gradebook_models import CourseSummary, GradeSummary
from api_client.group_api import get_users_in_group
from api_client.json_object import JsonObject, DataOnly
from api_client.json_object import JsonParser
from api_client.project_models import Project
from api_client.user_api import USER_ROLES, workgroup_models
from api_data_manager.course_data import CourseDataManager, COURSE_PROPERTIES
from lib.utils import PriorIdConvert

log = logging.getLogger(__name__)


# warnings associated with members generated from json response
# pylint: disable=maybe-no-member


# logic functions - recieve api implementor for test
class AcademyGradeAssessmentType(JsonObject):
    @property
    def type_name(self):
        return self.type[len(settings.GROUP_PROJECT_IDENTIFIER):] if self.is_group_assessment else self.type

    @property
    def is_group_assessment(self):
        return self.type.startswith(settings.GROUP_PROJECT_IDENTIFIER)


class AcademyGradePolicy(JsonObject):
    object_map = {
        "GRADER": AcademyGradeAssessmentType,
        "GRADE_CUTOFFS": DataOnly,
    }


class AcademyGradebook(JsonObject):
    object_map = {
        "courseware_summary": CourseSummary,
        "grade_summary": GradeSummary,
        "grading_policy": AcademyGradePolicy,
    }


class UserGrade(JsonObject):
    @property
    def user_grade_value(self):
        return self.grade if hasattr(self, "grade") and self.grade is not None else 0

    @property
    def user_grade_display(self):
        return round_to_int(self.user_grade_value)


class Proficiency(JsonObject):
    object_map = {
        "leaders": UserGrade,
    }

    @property
    def user_grade_value(self):
        return self.user_grade if hasattr(self, "user_grade") and self.user_grade is not None else 0

    @property
    def user_grade_display(self):
        return round_to_int(100 * self.user_grade_value)

    @property
    def course_average_value(self):
        return self.course_avg if hasattr(self, "course_avg") and self.course_avg is not None else 0

    @property
    def course_average_display(self):
        return round_to_int_bump_zero(100 * self.course_average_value)

    @property
    def has_leaders(self):
        return hasattr(self, 'leaders') and len(self.leaders) > 0 and self.leaders[0].grade > 0

    def pass_rate_display(self, users_with_roles):
        pass_users = 0
        for user_grade in self.leaders:
            if str(user_grade.id) not in users_with_roles:
                if user_grade.user_grade_value >= 0.7:
                    pass_users += 1

        return pass_users

    def pass_rate_display_for_company(self, users_with_roles, company_ids):
        pass_users = 0
        for user_grade in self.leaders:
            if user_grade.id in company_ids:
                if str(user_grade.id) not in users_with_roles:
                    if user_grade.user_grade_value >= 0.7:
                        pass_users += 1

        return pass_users

    def course_proficiency(self, users_with_roles):
        course_proficiency_sum = 0
        for user_grade in self.leaders:
            if str(user_grade.id) not in users_with_roles:
                user_proficiency = float(user_grade.user_grade_value) * 100
                course_proficiency_sum += user_proficiency
        return course_proficiency_sum

    def course_proficiency_for_company(self, users_with_roles, company_ids):
        course_proficiency_sum = 0
        for user_grade in self.leaders:
            if user_grade.id in company_ids:
                if str(user_grade.id) not in users_with_roles:
                    user_proficiency = float(user_grade.user_grade_value) * 100
                    course_proficiency_sum += user_proficiency
        return course_proficiency_sum


class UserProgress(JsonObject):
    @property
    def user_progress_value(self):
        return getattr(self, "completions", 0)

    @property
    def user_progress_display(self):
        return round_to_int(self.user_progress_value)


class Progress(UserProgress):
    object_map = {
        "leaders": UserProgress,
    }

    @property
    def course_average_value(self):
        return getattr(self, "course_avg", 0)

    @property
    def course_average_display(self):
        return round_to_int_bump_zero(self.course_average_value)

    @property
    def has_leaders(self):
        return hasattr(self, 'leaders') and len(self.leaders) > 0 and self.leaders[0].user_progress_value > 0

    def completion_rate_display(self, users):
        completed_users = 0
        users_ids = [user['id'] for user in users]
        for user_progress in self.leaders:
            if user_progress.id in users_ids:
                if user_progress.user_progress_value >= 100:
                    completed_users += 1
        return round_to_int_bump_zero(100 * completed_users / len(users))


class Social(JsonObject):
    object_map = {
        "leaders": JsonObject,
    }

    @property
    def course_average_value(self):
        return getattr(self, "course_avg", 0)

    @property
    def course_average_display(self):
        return round_to_int_bump_zero(self.course_average_value)


class CourseMetricsLeaders(JsonObject):
    object_map = {
        "grades": Proficiency,
        "completions": Progress,
        "social": Social,
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

    course = copy.deepcopy(load_course(course_id, MINIMAL_COURSE_DEPTH, course_api_impl, request=request))

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
    except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
        course_detail = False

    if course_detail is False or not hasattr(course_detail, 'position_tree'):
        return None

    return course_detail.position_tree


def get_chapter_and_target_by_location(request, course_id, location_id, course_api_impl=course_api):
    '''
    Returns chapter, vertical, and final target id for a given course and location.
    '''
    nav = course_api_impl.get_course_navigation(course_id, location_id)

    # If the course doesn't exist
    if nav is None:
        return None, None, None

    return nav.chapter, nav.vertical, nav.final_target_id


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
    course = load_course(course_id, MINIMAL_COURSE_DEPTH, course_api_impl, request=request)
    if not course.started:
        return course_id, None, None

    chapter = None
    page = None

    position_tree = get_course_position_tree(user_id, course_id, user_api_impl)
    if chapter_id is None:
        chapter_id = position_tree.chapter.id if position_tree and hasattr(position_tree, "chapter") else None
    chapter_candidates = [c for c in course.chapters if c.id == chapter_id]
    if len(chapter_candidates) > 0:
        chapter = chapter_candidates[0]

    if chapter is None and len(course.chapters) > 0:
        chapter = course.chapters[0]

    if chapter and chapter.sequentials:
        last_sequential_id = position_tree.sequential.id if position_tree and hasattr(position_tree,
                                                                                      "sequential") else None
        sequential_candidates = [s for s in chapter.sequentials if s.id == last_sequential_id]
        if len(sequential_candidates) > 0 and sequential_candidates[0].pages:
            last_page_id = position_tree.vertical.id if position_tree and hasattr(position_tree, "vertical") else None
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


def get_group_project_for_user_course(user_id, course, workgroup_id=None):
    '''
    Returns correct group and project information for the user for this course
    '''
    # Find the user_group(s) with which this user is associated

    if workgroup_id:
        workgroup = workgroup_api.get_workgroup(workgroup_id, workgroup_models.Workgroup)
        workgroup.project = project_api.get_project_url_by_id(workgroup.project)
        user_workgroups = [workgroup]
    else:
        user_workgroups = user_api.get_user_workgroups(user_id, course.id)

    if len(user_workgroups) < 1:
        return None, None

    project_group = user_workgroups[0]

    user_ids = [str(user.id) for user in workgroup_api.get_workgroup_users(project_group.id)]
    additional_fields = ["title", "first_name", "last_name", "profile_image"]
    project_group.members = user_api.get_users(ids=user_ids, fields=additional_fields)

    the_user_project = Project.fetch_from_url(project_group.project)
    group_project = None
    gp_candidates = [proj for proj in course.group_projects if proj.id == the_user_project.content_id]
    if gp_candidates:
        group_project = gp_candidates[0]
    return project_group, group_project


def get_group_project_for_workgroup_course(workgroup_id, course):
    '''
    Returns group and project information for the supplied workgroup
    '''
    workgroup = WorkGroup.fetch(workgroup_id)
    user_ids = [str(user.id) for user in workgroup.users]
    additional_fields = ["title", "first_name", "last_name", "profile_image"]
    workgroup.members = user_api.get_users(ids=user_ids, fields=additional_fields)
    project = Project.fetch(workgroup.project)
    group_project = [proj for proj in course.group_projects if proj.id == project.content_id][0]

    return workgroup, group_project


def group_project_location(group_project, sequential_id=None):
    '''
    Returns current sequential_id and page_id for the user for their group project
    '''
    if not group_project.activities:
        return None, None

    if group_project.is_v2:
        return None, group_project.id.replace('/', ';_')  # activities works differently in GP V2

    activity = group_project.activities[0]
    for act in group_project.activities:
        # is it the chosen one
        if act.id == sequential_id:
            activity = act

        # Is it a group_project xblock
        act.is_group_activity = is_group_activity(activity)

    if hasattr(activity, 'pages'):
        page = activity.pages[0] if len(activity.pages) > 0 else None
        usage_id = page.vertical_usage_id() if page else None
    else:
        usage_id = activity.id.replace('/', ';_')

    return activity, usage_id


def load_static_tabs(course_id, name=None):
    if name:
        # first try getting from thread local
        course_tabs = get_static_tab_context()

        # look into cache then
        if course_tabs is None:
            data_property = '{}_{}'.format(COURSE_PROPERTIES.TABS, 'details')
            course_tabs = CourseDataManager(course_id=course_id).get_cached_data(
                property_name=data_property,
                parsers=[
                    {'method': JsonParser.from_json, 'params': CourseTabs},
                    {'method': tabs_post_process},
                ]
            )

        if course_tabs is not None:
            course_tab = course_tabs.get(name)
        else:
            course_tabs = course_api.get_course_tabs(course_id, details=False)
            course_tab = course_tabs.get(name)
            if course_tab:
                course_tab = course_api.get_course_tab(course_id, tab_id=course_tab.id)

        return course_tab
    else:
        course_tabs = course_api.get_course_tabs(course_id, details=True)
        set_static_tab_context(course_tabs)
        return course_tabs


def round_to_int(value):
    return int(round(value))


def round_to_int_bump_zero(value):
    rounded_value = round_to_int(value)
    if rounded_value < 1 and value > 0:
        rounded_value = 1
    return rounded_value


def _individual_course_progress_metrics(course_id, user_id):
    return course_api.get_course_metrics_completions(
        course_id,
        user_id=user_id,
        completions_object_type=Progress,
        skipleaders=True
    )


def organization_course_progress_user_list(course_id, organization_id, count=3):
    return course_api.get_course_metrics_completions(
        course_id,
        organizations=organization_id,
        count=count,
        completions_object_type=Progress
    ).leaders


def return_course_progress(course, user_id):
    return _individual_course_progress_metrics(course.id, user_id).user_progress_display


def average_progress(course, user_id):
    return _individual_course_progress_metrics(course.id, user_id).course_average_display


def progress_percent(completion_count, module_count):
    if module_count > 0:
        return round_to_int(100 * completion_count / module_count)
    else:
        return 0


def group_project_reviews(user_id, course_id, project_workgroup, group_project):
    '''
    Returns group work reviews & average score for a project
    '''

    def mean(array_values):
        return sum(array_values) / float(len(array_values)) if len(array_values) > 0 else None

    review_items = WorkGroup.get_workgroup_review_items(project_workgroup.id)

    # workgroup review assignments
    assignment_count = 0
    assignments = ReviewAssignmentGroup.list_for_workgroup(project_workgroup.id)

    # find group activities in this project
    for activity in group_project.activities:
        group_project_xblock = get_group_activity_xblock(activity)
        activity_reviews = [item for item in review_items if group_project_xblock.id == item.content_id]

        assignment_count = 0
        for assignment in assignments:
            if assignment.data.xblock_id == group_project_xblock.id:
                assignment_count += len(get_users_in_group(assignment.id))

        # distinct reviewers
        reviewer_ids = set([ar.reviewer for ar in activity_reviews])

        # average by reviewer
        activity.grades = []
        for reviewer_id in reviewer_ids:
            grades = [int(review.answer) for review in activity_reviews if
                      reviewer_id == review.reviewer and is_number(review.answer)]
            activity.grades.append(mean(grades))

        activity.pending_grades = [0] * (assignment_count - len(activity.grades))
        activity.is_pending = len(activity.pending_grades) > 0

        # average score for this activity
        activity.score = mean(filter(None, activity.grades))

    group_work_avg = mean([a.score for a in group_project.activities if a.score is not None])
    return group_project.activities, group_work_avg


def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    return True


def get_proficiency_leaders(course_id, user_id, count=3):
    """
    If you need it along with progress or social leaders, please use `get_leaders`.
    """
    proficiency = course_api.get_course_metrics_grades(
        course_id, user_id=user_id, grade_object_type=Proficiency, count=count
    )
    if hasattr(proficiency, "leaders"):
        tailor_leader_list(proficiency.leaders)
    return proficiency


def get_progress_leaders(course_id, user_id):
    """
    If you need it along with proficiency or social leaders, please use `get_leaders`.
    """
    completions = course_api.get_course_metrics_completions(
        course_id, user_id=user_id, completions_object_type=Progress
    )
    tailor_leader_list(completions.leaders)
    return completions


def tailor_leader_list(leaders):
    for rank, leader in enumerate(leaders, 1):
        leader.rank = rank
        if hasattr(leader, 'grade'):
            leader.grade_display_value = round_to_int(100 * leader.grade)
        if hasattr(leader, 'score'):
            leader.points = leader.score


def social_total(social_metrics):
    social_total = 0

    for key, val in settings.SOCIAL_METRIC_POINTS.iteritems():
        social_total += getattr(social_metrics, key, 0) * val

    return social_total


def get_course_social_metrics(course_id):
    """
    Returns social metrics against all users in a course.
    """
    return course_api.get_course_social_metrics(course_id)


def get_user_social_metrics(user_id, course_id, include_stats=False):
    """
    :param course_id:
    :param user_id:
    :param include_stats: a boolean value to indicate if we needs social stats also
        social stats contains a dict with these keys
        num_threads, num_thread_followers, num_replies, num_flagged, num_comments, num_threads_read,
        num_downvotes, num_upvotes, num_comments_generated
    :return: a dict having user's social metrics for given course
    """
    default_metrics = None
    if include_stats:
        default_metrics = JsonParser.from_dictionary({
            key: 0
            for key in ['num_threads', 'num_thread_followers', 'num_replies',
                        'num_flagged', 'num_comments', 'num_threads_read',
                        'num_downvotes', 'num_upvotes', 'num_comments_generated']
        })
    data = {'points': 0, 'course_avg': 0, 'metrics': default_metrics}
    try:
        metrics = user_api.get_course_social_metrics(user_id, course_id, include_stats)
        data = {
            'points': metrics.score,
            'course_avg': round_to_int_bump_zero(metrics.course_avg),
            'metrics': getattr(metrics, 'stats', None)
        }
    except ApiError as error:
        log.exception(
            u"Error getting user social metrics. course_id=%s, user_id=%s, include_stats=%s, error=%s",
            course_id,
            user_id,
            include_stats,
            error,
        )
    return data


def get_social_leaders(course_id, user_id, count=3):
    """
    If you need it along with proficiency or progress leaders, please use `get_leaders`.
    :param course_id:
    :param user_id:
    :param count:
    :return: returns course social leaderboard upto to limit given in count and rank of given user in leaderboard
    """
    data = {'points': 0, 'course_avg': 0, 'position': 0, 'leaders': []}
    try:
        metrics = course_api.get_social_engagement_leaderboard(course_id, count, user_id=user_id)
        tailor_leader_list(metrics.leaders)
        data = {
            'points': metrics.score,
            'course_avg': round_to_int_bump_zero(metrics.course_avg),
            'position': metrics.position,
            'leaders': metrics.leaders
        }
    except ApiError as error:
        log.exception(
            u"Error getting social engagement leaderboard. course_id=%s, user_id=%s, count=%s, error=%s",
            course_id,
            user_id,
            count,
            error,
        )
    return data


def get_leaders(**kwargs):
    """
    Get completions, proficiency and social metrics in one request.
    :param kwargs:
        - `course_id`
        - `user_id`
        - `count`
    """
    try:
        data = course_api.get_course_metrics_leaders(**kwargs)
        tailor_leader_list(data.grades.leaders)
        tailor_leader_list(data.completions.leaders)
        tailor_leader_list(data.social.leaders)
    except ApiError as error:
        log.exception(
            u"Error getting leaders. course_id=%s, user_id=%s, count=%s, error=%s",
            kwargs.get('course_id'),
            kwargs.get('user_id'),
            kwargs.get('count'),
            error,
        )
        raise error

    return data


def get_ta_users(course_id, course_role_users=None):
    role = USER_ROLES.TA
    role_users = course_role_users or course_api.get_users_filtered_by_role(course_id)
    ta_users_base = [str(user.id) for user in role_users if user.role == role]
    additional_fields = ["title", "profile_image", "city", "full_name"]
    ta_users = user_api.get_users(ids=ta_users_base, fields=additional_fields) if ta_users_base else []
    return ta_users


def choose_random_ta(course_id, course_role_users=None):
    ta_users = [user for user in get_ta_users(course_id, course_role_users) if user.city]
    return random.choice(ta_users) if ta_users else None


def load_lesson_estimated_time(course):
    estimated_time = load_static_tabs(course.id, name="estimated time")

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
                if section.graded is True:
                    points = section.section_total[0]
                    max_points = section.section_total[1]
                    if max_points > 0:
                        percent = round_to_int(100 * points / max_points)
                    else:
                        percent = 0
                    assesments[section.url_name] = percent

    for lesson in course.chapters:
        lesson.assesment_score = None
        for sequential in lesson.sequentials:
            url_name = PriorIdConvert.new_from_prior(sequential.id).split('/')[-1]
            if url_name in assesments:
                lesson.assesment_score = assesments[url_name]
                sequential.assesment_score = assesments[url_name]

    for project in course.group_projects:
        for activity in project.activities:
            if project.is_v2:
                activity.is_graded = activity.xblock.weight > 0
            else:
                activity.is_graded = False
                url_name = PriorIdConvert.new_from_prior(activity.id).split('/')[-1]
                if url_name in assesments:
                    activity.is_graded = True

    return gradebook


def add_months_to_date(new_date, months):
    month = new_date.month - 1 + months
    year = int(new_date.year + month / 12)
    month = month % 12 + 1
    return datetime(year, month, 1)


def progress_update_handler(request, course, chapter_id=None, page_id=None):
    '''
    Triggered by user visiting the module. Filters tiles with current course_ids.
    Updates progress only for current module and parent lesson/course.
    '''
    tiles = LearnerDashboardTile.objects.filter(link__icontains=course.id)
    if chapter_id:
        kwargs = {'root_block': chapter_id}
    else:
        kwargs = {}

    course_completions = {}
    completions = course_api.get_course_completions(course.id, request.user.username, **kwargs)
    if completions and tiles:
        for tile in tiles:
            link = strip_tile_link(tile.link)
            if link:
                if (tile.tile_type == '3' or tile.tile_type == '5') and page_id not in tile.link:
                    continue
                if tile.tile_type == '2' and chapter_id not in tile.link:
                    continue
                if tile.tile_type == '7' and not link['block_id'] in tile.link:
                    continue
                if tile.tile_type == '4' and chapter_id is not None:
                    if course.id not in course_completions:
                        completion = course_api.get_course_completions(
                            course.id,
                            request.user.username,
                            extra_fields=''
                        )
                        course_completions[course.id] = completion
                    update_progress(tile, request.user, course, course_completions[course.id], link)
                    continue

                update_progress(
                    tile,
                    request.user,
                    course,
                    completions,
                    link,
                )


def get_completion_percentage_from_id(completions, aggregation, block_key=None):
    if aggregation == 'course':
        percentage = completions.get('completion', {}).get('percent', 0.)
    else:
        percentage = completions.get(block_key, {}).get('completion', {}).get('percent', 0.)
    if percentage is None:
        percentage = 0.0
    return round_to_int(percentage * 100)


def update_progress(tile, user, course, completions, link):
    if isinstance(user, dict):
        user_completions = completions.get(user["username"], {})
        user_id = user['id']
    else:
        user_completions = completions.get(user.username, {})
        user_id = user.id

    obj, created = LearnerDashboardTileProgress.objects.get_or_create(
        milestone=tile,
        user=user_id,
    )

    if tile.tile_type == '4':
        obj.percentage = get_completion_percentage_from_id(user_completions, 'course')
        set_user_course_progress(course, user_completions)
    elif tile.tile_type == '2':
        obj.percentage = get_completion_percentage_from_id(
            user_completions,
            'chapter',
            link['lesson_id'],
        )
        set_user_course_progress(course, user_completions, chapter_id=link['lesson_id'])
    elif tile.tile_type == '3' or tile.tile_type == '5':
        obj.percentage = get_completion_percentage_from_id(
            user_completions,
            'sequential',
            link['page_id'],
        )
    elif tile.tile_type == '7' and link['block_id']:
        obj.percentage = calculate_user_group_activity_progress(user, course, link['block_id'])
    obj.save()


def calculate_user_group_activity_progress(user, course, link):
    username = getattr(user, 'username', None) or user['username']
    block_completions = course_api.get_block_completions(
        course_id=course.id,
        username=username,
    )

    completed_ids = [
        block.id
        for block in block_completions
        if block.is_complete()
    ]
    user_id = getattr(user, 'id', None) or user['id']
    project_group, group_project = get_group_project_for_user_course(user_id, course)

    if group_project:
        for activity in group_project._activities:
            activity_response = workgroup_api.get_groupwork_activity(activity.uri)
            stage_ids = [stage.id for stage in activity_response.children if "peer-review" not in stage.id]
            if link in stage_ids:
                matches = set(stage_ids).intersection(completed_ids)
                return round_to_int(100 * len(matches) / len(stage_ids))
    else:
        return 0


def set_user_course_progress(course, completions, chapter_id=None):
    for lesson in course.chapters:
        if chapter_id is None or lesson.id == chapter_id:
            lesson.progress = get_completion_percentage_from_id(
                completions,
                'chapter',
                lesson.id,
            )
            for sequential in lesson.sequentials:
                sequential.progress = get_completion_percentage_from_id(
                    completions,
                    'sequential',
                    sequential.id,
                )
                for module in sequential.children:
                    module.progress = get_completion_percentage_from_id(
                        completions,
                        'vertical',
                        module.id,
                    )
                    module.is_complete = module.progress == 100


def get_course_object(user_id, course_id):
    courses = user_api.get_user_courses(user_id)
    course = [c for c in courses if c.id == course_id]
    if course:
        return load_course(course[0].id, depth=MINIMAL_COURSE_DEPTH)
    else:
        return None


def strip_tile_link(link):
    # TODO: Refactor!!!

    if link.startswith("/learnerdashboard/"):
        link = link[17:]

    if link.endswith("/lesson/") or link.endswith("/module/"):
        link = link[:-8]

    discussion = re.search('/discussion(.*)$', link)
    if discussion:
        link = link.replace(discussion.group(0), "")

    resources = re.search('/resources(.*)$', link)
    if resources:
        link = link.replace(resources.group(0), "")

    gw_activity = re.search('activate_block_id(.*)$', str(link))
    if gw_activity:
        substring_course_id = re.search('/courses/(.*)/group_work', link)
        course_id = substring_course_id.group(1)

        substring_block_id = re.search('activate_block_id=(.*)', link)
        block_id = substring_block_id.group(1)

        stripped_link = {
            'course_id': course_id,
            'lesson_id': None,
            'page_id': None,
            'block_id': block_id,
        }
        return stripped_link

    try:
        substring = re.search('/courses/(.*)/lessons/', link)
        course_id = substring.group(1)
    except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
        stripped_link = {
            'course_id': link.replace("/courses/", ""),
            'lesson_id': None,
            'page_id': None,
            'block_id': None,
        }
        return stripped_link

    substring = re.search('/lessons/(.*)/module/', link)
    lesson_id = substring.group(1)

    substring = re.search('/module/(.*)$', link)
    page_id = substring.group(1)

    stripped_link = {
        'course_id': course_id,
        'lesson_id': lesson_id,
        'page_id': page_id,
        'block_id': None,
    }
    return stripped_link


def createProgressObjects(progressData, tile_ids, user_id):
    progress_ids = [str(i.milestone.id) for i in progressData]
    tiles = list(set(tile_ids) - set(progress_ids))

    for tile in tiles:
        obj, created = LearnerDashboardTileProgress.objects.get_or_create(
            milestone_id=int(tile),
            user=user_id,
            percentage=0,
        )


def _remove_duplicate_grader(graders):
    """
    Removes duplicate graders, used for private group work configuration.
    """
    for i in range(0, len(graders)):
        for j in range(i + 1, len(graders)):
            if compare_graders(graders[i], graders[j]):
                graders.pop(i)
                break


def compare_graders(a, b):
    if (a.weight == b.weight) and ("GROUP_PROJECT_" in str(a.type)) and ("GROUP_PROJECT_" in str(b.type)):
        return True
    else:
        return False


def fix_resource_page_video_scripts(resources_page_html):
    """
    Removes Ooyala Player V3 script occurrences and include
    V4 script file in resources page HTML
    """
    resource_page_soup = BeautifulSoup(resources_page_html, "html.parser")
    v4_script = resource_page_soup.new_tag("script", src=settings.OOYALA_PLAYER_V4_SCRIPT_FILE)

    for script_tag in resource_page_soup.find_all('script'):
        if 'player.ooyala.com/v3/' in script_tag.attrs.get('src', ''):
            script_tag.decompose()

    # include v4 script at the top of the page
    resource_page_soup.insert(0, v4_script)

    return str(resource_page_soup)


def get_assessment_module_name_translation(module_name):
    """ Translates assessment part of the module name """
    if module_name.startswith("Assessment"):
        return module_name.replace("Assessment", _("Assessment"))
    return module_name


def get_non_staff_user(course_id):
    """
    Returns a non-staff (with no role) user in a course
    """
    non_staff_user = None

    course_users = course_api.get_course_details_users(course_id, {'fields': 'id,username,is_staff'})['results']
    course_role_user_ids = [user.id for user in course_api.get_users_filtered_by_role(course_id)]

    for user in course_users:
        if user.get('id') not in course_role_user_ids and not user.get('is_staff'):
            non_staff_user = user
            break

    return non_staff_user


def get_learner_dashboard(request, course_id):

    learner_dashboard = None

    if settings.LEARNER_DASHBOARD_ENABLED:
        feature_flags = CourseDataManager(course_id).get_feature_flags()
        if feature_flags.learner_dashboard:
            organization = get_basic_user_data(request.user.id).organization
            if organization:
                request.session['client_display_name'] = organization.display_name
                try:
                    learner_dashboard = LearnerDashboard.objects.get(course_id=course_id)
                except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
                    pass
    return learner_dashboard


def user_learner_dashboards(request, user_courses):
    learner_dashboards = []
    if settings.LEARNER_DASHBOARD_ENABLED:
        for course in user_courses:
            dashboard = None
            try:
                dashboard = LearnerDashboard.objects.get(course_id=course.id)
            except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
                pass
            if dashboard:
                calendar_items = LearnerDashboardTile.objects.filter(
                    learner_dashboard=dashboard.id, show_in_calendar=True
                )
                dashboard.calendar_enabled = True if calendar_items else False
                dashboard.features = CourseDataManager(course.id).get_feature_flags()
                learner_dashboards.append(dashboard)

    return learner_dashboards
