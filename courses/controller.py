''' Core logic to sanitise information for views '''
from api_client import course_api, user_api

# warnings associated with members generated from json response
# pylint: disable=maybe-no-member


def _is_int_equal(elem1, elem2):
    ''' tests equality of integer values; upon error tests simple equality '''
    result = False
    try:
        result = (int(elem1) == int(elem2))
    except ValueError:
        result = (elem1 == elem2)

    return result

# logic functions - recieve api implementor for test


def build_page_info_for_course(course_id, chapter_id, page_id, course_api_impl=course_api):
    '''
    Returns course structure and user's status within course
        course_api_impl - optional api client module to use (useful in mocks)
    '''
    course = course_api_impl.get_course(course_id)

    # something sensible if we fail...
    current_chapter = course.chapters[0]
    current_page = None

    prev_page = None
    for chapter in course.chapters:
        chapter.navigation_url = '/courses/{}/lessons/{}'.format(
            course_id,
            chapter.chapter_id
        )
        if _is_int_equal(chapter.chapter_id, chapter_id):
            current_chapter = chapter

        for page in chapter.pages:
            page.prev_url = None
            page.next_url = None
            page.navigation_url = '{}/module/{}'.format(
                chapter.navigation_url, page.page_id)

            if _is_int_equal(page.page_id, page_id):
                current_page = page

            if prev_page is not None:
                page.prev_url = prev_page.navigation_url
                prev_page.next_url = page.navigation_url
            prev_page = page

    if not current_page:
        current_page = current_chapter.pages[0]

    return course, current_chapter, current_page


def locate_chapter_page(user_id, course_id, chapter_id, user_api_impl=user_api, course_api_impl=course_api):
    '''
    Returns current chapter and page for given course from user's status
    Chapter defaults to bookmark if not provided, to 1st chapter if no bookmark
    Page defaults to bookmark if not provided, to 1st page if no bookmark
        course_api_impl - optional api client module to use (useful in mocks)
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    user_status = user_api_impl.get_user_course_status(user_id)
    if not course_id:
        course_id = user_status.current_course_id

    bookmark = user_status.get_bookmark_for_course(course_id)
    if bookmark is not None and (chapter_id is None or bookmark.chapter_id == chapter_id):
        return course_id, bookmark.chapter_id, bookmark.page_id

    course = course_api_impl.get_course(course_id)
    chapter = course.chapters[0]
    if chapter_id:
        for course_chapter in course.chapters:
            if course_chapter.chapter_id == chapter_id:
                chapter = course_chapter
                break
    page = chapter.pages[0]

    return course_id, chapter.chapter_id, page.page_id


def program_for_course(user_id, course_id, user_api_impl=user_api):
    '''
    Returns first program that contains given course for this user,
    or None if program is not present
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    user_status = user_api_impl.get_user_course_status(user_id)
    course_program = None

    # Check that the specified course is part of this program
    for program in user_status.programs:
        if int(course_id) in program.courses:
            course_program = program
            break

    # Now add the courses therein:
    if course_program:
        course_ids = course_program.courses
        course_program.courses = []
        for course in user_status.courses:
            if int(course.course_id) in course_ids:
                course_program.courses.append(course)

    return course_program


# pylint: disable=too-many-arguments
def update_bookmark(user_id, program_id, course_id, chapter_id, page_id, user_api_impl=user_api):
    '''
    Informs the openedx api of user's location
        user_api_impl - optional api client module to use (useful in mocks)
    '''
    user_api_impl.set_user_bookmark(
        user_id,
        program_id,
        course_id,
        chapter_id,
        page_id
    )
