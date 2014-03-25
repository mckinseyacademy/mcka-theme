from api_client import course_api, user_api

def _is_int_equal(elem1, elem2):
    result = False
    try:
        result = (int(elem1) == int(elem2))
    except:
        result = (elem1 == elem2)

    return result

# logic functions - recieve api implementor for test
def build_page_info_for_course(course_id, chapter_id, page_id, course_api = course_api):
    course = course_api.get_course(course_id)

    # something sensible if we fail...
    current_chapter = course.chapters[0]
    current_page = None

    prev_page = None
    for chapter in course.chapters:
        chapter.navigation_url = '/courses/{}/lessons/{}'.format(course_id, chapter.chapter_id)
        if _is_int_equal(chapter.chapter_id, chapter_id):
            current_chapter = chapter

        for page in chapter.pages:
            page.prev_url = None
            page.next_url = None
            page.navigation_url = '{}/module/{}'.format(chapter.navigation_url, page.page_id)

            if _is_int_equal(page.page_id, page_id):
                current_page = page

            if None != prev_page:
                page.prev_url = prev_page.navigation_url
                prev_page.next_url = page.navigation_url
            prev_page = page

    if not current_page:
        current_page = current_chapter.pages[0]

    return course, current_chapter, current_page


def locate_chapter_page(user_id, course_id, chapter_id, user_api = user_api, course_api = course_api):
    user_status = user_api.get_user_course_status(user_id)
    if not course_id:
        course_id = user_status.current_course_id

    bookmark = user_status.get_bookmark_for_course(course_id)
    if None != bookmark and (chapter_id == None or bookmark.chapter_id == chapter_id):
        return course_id, bookmark.chapter_id, bookmark.page_id

    course = course_api.get_course(course_id)
    chapter = course.chapters[0]
    if chapter_id:
        for course_chapter in course.chapters:
            if course_chapter.chapter_id == chapter_id:
                chapter = course_chapter
                break
    page = chapter.pages[0]

    return course_id, chapter.chapter_id, page.page_id