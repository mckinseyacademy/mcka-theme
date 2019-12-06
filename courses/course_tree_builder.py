from django.utils.translation import get_language_bidi
from django.conf import settings

from api_client import user_api
from api_client import course_api
from api_data_manager.course_data import CourseDataManager, COURSE_PROPERTIES

from .controller import (
    load_course, load_static_tabs,
    get_completion_percentage_from_id,
    locate_chapter_page,
    inject_gradebook_info,
    set_user_course_progress,
)


class CourseTreeBuilder(object):
    """
    Utility class for building course tree structure
    """
    def __init__(self, course_id, request):
        self.course_id = course_id
        self.request = request
        self.course = None
        self.current_lesson_id = None
        self.current_module_id = None

        if request and request.resolver_match:
            self.current_lesson_id = request.resolver_match.kwargs.get('chapter_id', None)
            self.current_module_id = request.resolver_match.kwargs.get('page_id', None)

    def _load_course(self):
        return load_course(course_id=self.course_id, request=self.request)

    def get_processed_course(self):
        self.course = self._load_course()
        self.build_page_info()
        self.include_progress_data()
        self.include_lesson_descriptions()

        return self.course

    def get_processed_course_static_data(self):
        """
        only returns non-dynamic course tree data
        i.e; course tree, lesson estimated times and descriptions
        """
        self.course = self._load_course()
        load_static_tabs(course_id=self.course_id)
        self.include_lesson_descriptions()

        return self.course

    def get_processed_course_dynamic_data(self, course=None):
        """
        only return dynamic/user-related course data
        """
        course = course or self.course

        self.build_page_info(course)
        self.include_progress_data(course=course)

        return course

    def build_page_info(self, course=None):
        """
        Sets current lesson, bookmarks and navigation urls
        on passed course object
        """
        course = course or self.course

        if len(course.chapters) < 1:
            return course

        if None in (self.current_module_id, self.current_lesson_id):
            course_id, self.current_lesson_id, page_id = locate_chapter_page(
                self.request, self.request.user.id,
                self.course_id, None
            )

        # Set default current lesson just in case
        course.current_lesson = course.chapters[0]

        previous_module = None
        next_module = None

        # Inject lesson information for course
        for idx, lesson in enumerate(course.chapters, start=1):
            lesson.index = idx
            lesson.navigation_url = '/courses/{}/lessons/{}'.format(self.course_id, lesson.id)
            lesson.module_count = 0
            lesson.modules = []

            # Set current lesson and lesson bookmark
            if lesson.id == self.current_lesson_id:
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

                if self.current_module_id == module.id:
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

    def include_progress_data(self, course=None, chapter_id=None):
        course = course or self.course

        username = user_api.get_user(self.request.user.id).username
        completions = course_api.get_course_completions(course.id, username)
        user_completions = completions.get(username, {})
        course.user_progress = get_completion_percentage_from_id(user_completions, 'course')
        set_user_course_progress(course, user_completions, chapter_id)

    def include_lesson_descriptions(self, course=None):
        course = course or self.course
        static_tabs = load_static_tabs(course.id)
        for idx, lesson in enumerate(course.chapters, start=1):
            lesson_description = static_tabs.get("lesson{}".format(idx))
            if lesson_description:
                lesson.description = lesson_description.content

        estimated_time = static_tabs.get("estimated time")
        if estimated_time:
            estimates = [s.strip() for s in estimated_time.content.splitlines()]
            for idx, lesson in enumerate(course.chapters):
                if idx < len(estimates):
                    lesson.estimated_time = estimates[idx]

    def get_module_navigators(self, course=None):
        course = course or self.course

        current_lesson = getattr(course, 'current_lesson', None)
        right_lesson_module_navigator = getattr(current_lesson, 'next_module', None)
        left_lesson_module_navigator = getattr(current_lesson, 'previous_module', None)

        if get_language_bidi():
            right_lesson_module_navigator, left_lesson_module_navigator = left_lesson_module_navigator, \
                                                                          right_lesson_module_navigator

        return right_lesson_module_navigator, left_lesson_module_navigator

    def get_graded_items_count(self, course=None):
        course = course or self.course

        course_data_manager = CourseDataManager(course_id=self.course_id)

        graded_items_count = course_data_manager.get_cached_data(COURSE_PROPERTIES.GRADED_ITEMS_COUNT)

        if graded_items_count is None:
            inject_gradebook_info(self.request.user.id, course)
            graded_items_count = sum(len(graded) for graded in list(course.graded_items().values()))

            course_data_manager.set_cached_data(
                property_name=COURSE_PROPERTIES.GRADED_ITEMS_COUNT,
                data=graded_items_count,
                expiry_time=settings.CACHE_TIMEOUTS.get('longterm_course_data', settings.DEFAULT_CACHE_TIMEOUT)
            )

        return graded_items_count
