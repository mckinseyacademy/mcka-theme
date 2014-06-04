''' Core logic to sanitise information for views '''
#from urllib import quote_plus, unquote_plus

from django.conf import settings

from api_client import course_api, user_api, user_models
from api_client.api_error import ApiError
from license import controller as license_controller
from admin.models import Program, WorkGroup
from admin.controller import load_course

# warnings associated with members generated from json response
# pylint: disable=maybe-no-member


# logic functions - recieve api implementor for test

def build_page_info_for_course(
    course_id,
    chapter_id,
    page_id,
    chapter_position=None,
    course_api_impl=course_api
):
    '''
    Returns course structure and user's status within course
        course_api_impl - optional api client module to use (useful in mocks)
    '''
    course = load_course(course_id, 3, course_api_impl)

    # something sensible if we fail...
    if len(course.chapters) < 1:
        return course, None, None, None

    current_chapter = course.chapters[0]
    current_sequential = None
    current_page = None

    prev_page = None

    if chapter_position and len(course.chapters) >= chapter_position:
        course.chapters[chapter_position - 1].bookmark = True

    for chapter in course.chapters:
        chapter.navigation_url = '/courses/{}/lessons/{}'.format(course_id, chapter.id)
        if chapter.id == chapter_id:
            current_chapter = chapter

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


def get_course_position_information(user_id, course_id, user_api_impl=user_api):
    try:
        course_detail = user_api_impl.get_user_course_detail(user_id, course_id)
    except ApiError, e:
        course_detail = user_models.UserCourseStatus(dictionary={"position": None})

    return course_detail


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
    course = load_course(course_id, 3, course_api_impl)
    chapter = None
    page = None

    course_detail = get_course_position_information(user_id, course_id, user_api_impl)
    if course_detail.position and len(course.chapters) >= course_detail.position:
        chapter = course.chapters[course_detail.position - 1]
        chapter.bookmark = True
    elif len(course.chapters) > 0:
        chapter = course.chapters[0]

    if chapter_id:
        for course_chapter in course.chapters:
            if course_chapter.id == chapter_id:
                chapter = course_chapter
                break
    if chapter and chapter.sequentials and len(chapter.sequentials) > 0 and chapter.sequentials[0].pages and len(chapter.sequentials[0].pages) > 0:
        page = chapter.sequentials[0].pages[0]

    chapter_id = chapter.id if chapter else None
    page_id = page.id if page else None

    return course_id, chapter_id, page_id, course_detail.position


def program_for_course(user_id, course_id, user_api_impl=user_api):
    '''
    Returns first program that contains given course for this user,
    or None if program is not present
        user_api_impl - optional api client module to use (useful in mocks)
    '''

    courses = user_api_impl.get_user_courses(user_id)

    course_program = None
    for program in Program.programs_with_course(course_id):
        if license_controller.fetch_granted_license(program.id, user_id) is not None:
            course_program = program
            break

    if course_program:
        program_course_ids = [course.course_id for course in course_program.fetch_courses()]
        course_program.courses = [course for course in courses if course.id in program_course_ids]
        course_program.outside_courses = [course for course in courses if course.id not in program_course_ids]
    else:
        course_program = Program(dictionary={"id": "NO_PROGRAM", "name": settings.NO_PROGRAM_NAME})
        course_program.courses = courses
        course_program.outside_courses = None

    return course_program


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
    user_project_group_ids = [user_group.id for user_group in user_api.get_user_groups(user_id, "workgroup")]

    # Find the group_project to which one of these project groups is assigned:
    group_project = None
    project_group = None
    for project in course.group_projects:
        try:
            project_groups = course_api.get_course_content_groups(course.id, project.id)
        except:
            project_groups = []

        intersection_ids = [pg.group_id for pg in project_groups if pg.group_id in user_project_group_ids]
        if len(intersection_ids) > 0:
            group_project = project
            project_group = WorkGroup.fetch_with_members(intersection_ids[0])
            break;

    if not group_project:
        if len(course.group_projects) > 0:
            group_project = course.group_projects[0]
        else:
            return None, None, None, None

    # TODO - remove fake project group when desired
    if not project_group:
        # return None, group_project, None, None
        project_group = _fake_project_group()

    # Get the right location within this group project - can't do this yet
    #course_detail = get_course_position_information(user_id, course.id)

    sequential = group_project.sequentials[0]
    for seq in group_project.sequentials:
        # is it the chosen one
        if seq.id == sequential_id:
            sequential = seq

        # Is it a group_project xblock
        seq.is_group_project = len(sequential.pages) > 0 and "group-project" in sequential.pages[0].child_category_list()

    page = sequential.pages[0] if len(sequential.pages) > 0 else None

    return project_group, group_project, sequential, page
