''' Core logic to sanitise information for views '''
#from urllib import quote_plus, unquote_plus

from django.conf import settings

from accounts.middleware.thread_local import set_static_tab_context, get_static_tab_context

from api_client import course_api, user_api, user_models, workgroup_api
from api_client.api_error import ApiError
from api_client.project_models import Project
from admin.models import WorkGroup
from admin.controller import load_course

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


class ProjectGroup(object):
    members = []
    teaching_assistant = None

def _fake_project_group():
    members_list = [
        user_models.UserResponse(dictionary={
            "username": "jg",
            "first_name": "Jennifer",
            "last_name": "Gormley",
            "title": "Director of Product Design",
            "email": "Jennifer_Gormley@mckinsey.com",
            }),
        user_models.UserResponse(dictionary={
            "username": "ap",
            "first_name": "Andy",
            "last_name": "Parsons",
            "title": "CTO",
            "email": "Andy_Parsons@mckinsey.com",
            }),
        user_models.UserResponse(dictionary={
            "username": "vg",
            "first_name": "Vishal",
            "last_name": "Ghandi",
            "title": "Product Manager",
            "email": "vishalhgandhi@gmail.com",
            }),
        user_models.UserResponse(dictionary={
            "username": "jr",
            "first_name": "Jonathan",
            "last_name": "Rainey",
            "title": "Front End Specialist",
            "email": "tivoli@nurfed.com",
            }),
    ]
    ta = user_models.UserResponse(dictionary={
        "username": "ta",
        "first_name": "Your",
        "last_name": "TA",
        "title": "McKinsey Teaching Assistant",
        "email": "tas@mckinseyacademy.com",
    })
    project_group = ProjectGroup()
    project_group.members = members_list
    project_group.teaching_assistant = ta

    return project_group

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
