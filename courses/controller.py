''' Core logic to sanitise information for views '''
from api_client import course_api, user_api, user_models
#from urllib import quote_plus, unquote_plus

# warnings associated with members generated from json response
# pylint: disable=maybe-no-member


# logic functions - recieve api implementor for test


def decode_id(encoded_id):
    #return unquote_plus(encoded_id)
    return encoded_id.replace('___', '/')

def encode_id(plain_id):
    #return quote_plus(plain_id)
    return plain_id.replace('/', '___')

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
    course = course_api_impl.get_course(course_id)

    # something sensible if we fail...
    current_chapter = course.chapters[0]
    current_sequential = None
    current_page = None

    prev_page = None

    if chapter_position and len(course.chapters) >= chapter_position:
        course.chapters[chapter_position - 1].bookmark = True

    for chapter in course.chapters:
        chapter.navigation_url = '/courses/{}/lessons/{}'.format(
            encode_id(course_id),
            encode_id(chapter.id)
        )
        if chapter.id == chapter_id:
            current_chapter = chapter

        for sequential in chapter.sequentials:
            for page in sequential.pages:
                page.prev_url = None
                page.next_url = None
                page.navigation_url = '{}/module/{}'.format(
                    chapter.navigation_url, encode_id(page.id))

                if page.id == page_id:
                    current_page = page
                    current_sequential = sequential

                if prev_page is not None:
                    page.prev_url = prev_page.navigation_url
                    prev_page.next_url = page.navigation_url
                prev_page = page

    if not current_page:
        current_sequential = current_chapter.sequentials[0]
        current_page = current_sequential.pages[0]

    return course, current_chapter, current_sequential, current_page


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
    if not course_id:
        courses = user_api_impl.get_user_courses(user_id)
        if len(courses) < 1:
            return None, None, None
        course_id = courses[0].id

    course = course_api_impl.get_course(course_id)

    course_detail = user_api_impl.get_user_course_detail(user_id, course_id)
    if len(course.chapters) >= course_detail.position:
        chapter = course.chapters[course_detail.position - 1]
        chapter.bookmark = True
    else:
        chapter = course.chapters[0]

    if chapter_id:
        for course_chapter in course.chapters:
            if course_chapter.id == chapter_id:
                chapter = course_chapter
                break
    page = chapter.sequentials[0].pages[0]

    return course_id, chapter.id, page.id, course_detail.position


def program_for_course(user_id, course_id, user_api_impl=user_api):
    '''
    Returns first program that contains given course for this user,
    or None if program is not present
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    courses = user_api_impl.get_user_courses(user_id)
    course_program = user_models.UserProgram(dictionary={"id": "DEFAULT_PROGRAM", "name": "McKinsey Academy Program"})
    course_program.courses = courses

    # Check that the specified course is part of this program
    # for program in courses.programs:
    #     if course_id in [course.id for course in program.courses]:
    #         course_program = program
    #         break

    # # Now add the courses therein:
    # if course_program:
    #     course_ids = [course.id for course in course_program.courses]
    #     course_program.courses = []
    #     for course in courses.courses:
    #         if course.id in course_ids:
    #             course_program.courses.append(course)

    return course_program


# pylint: disable=too-many-arguments
def update_bookmark(user_id, program_id, course_id, chapter_id, sequential_id, page_id, user_api_impl=user_api):
    '''
    Informs the openedx api of user's location
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    user_api_impl.set_user_bookmark(
        user_id,
        program_id,
        course_id,
        chapter_id,
        sequential_id,
        page_id
    )
