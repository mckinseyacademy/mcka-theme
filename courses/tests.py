import traceback
import mock
from django.test import TestCase
from api_client import course_models, user_models
from django.core.urlresolvers import resolve

from . import controller

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name
from courses.user_courses import CURRENT_PROGRAM
from courses.views import infer_page_navigation


class UrlsTest(TestCase):

    def test_infer_course_navigation_url(self):
        resolver = resolve('/courses/c152/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')

        resolver = resolve('/courses/ABC/123/456/789/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

    def test_infer_chapter_navigation_url(self):
        resolver = resolve('/courses/c152/lessons/ch153')
        self.assertEqual(resolver.view_name, 'infer_chapter_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['chapter_id'], 'ch153')

        resolver = resolve('/courses/ABC/123/456/789/lessons/XYZ/987/654/321')
        self.assertEqual(resolver.view_name, 'infer_chapter_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['chapter_id'], 'XYZ/987/654/321')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons/i4x://edX/Open_DemoX/chapter/interactive_demonstrations')
        self.assertEqual(resolver.view_name, 'infer_chapter_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['chapter_id'], 'i4x://edX/Open_DemoX/chapter/interactive_demonstrations')

    def test_infer_page_navigation_url(self):
        resolver = resolve('/courses/c152/lessons/jump_to_page/ch153')
        self.assertEqual(resolver.view_name, 'infer_page_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['page_id'], 'ch153')

        resolver = resolve('/courses/ABC/123/456/789/lessons/jump_to_page/XYZ/987/654/321')
        self.assertEqual(resolver.view_name, 'infer_page_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['page_id'], 'XYZ/987/654/321')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons/jump_to_page/i4x://edX/Open_DemoX/page/interactive_demonstrations')
        self.assertEqual(resolver.view_name, 'infer_page_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['page_id'], 'i4x://edX/Open_DemoX/page/interactive_demonstrations')

    def test_navigate_to_lesson_module_url(self):
        resolver = resolve('/courses/c152/lessons/ch153/module/p154')
        self.assertEqual(resolver.view_name, 'navigate_to_lesson_module')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['chapter_id'], 'ch153')
        self.assertEqual(resolver.kwargs['page_id'], 'p154')

        resolver = resolve('/courses/ABC/123/456/789/lessons/XYZ/987/654/321/module/LMN/ZXC/LAKSJDFLASKJFLWE/444')
        self.assertEqual(resolver.view_name, 'navigate_to_lesson_module')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['chapter_id'], 'XYZ/987/654/321')
        self.assertEqual(resolver.kwargs['page_id'], 'LMN/ZXC/LAKSJDFLASKJFLWE/444')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons/i4x://edX/Open_DemoX/chapter/d8a6192ade314473a78242dfeedfbf5b/module/i4x://edX/Open_DemoX/sequential/edx_introduction')
        self.assertEqual(resolver.view_name, 'navigate_to_lesson_module')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['chapter_id'], 'i4x://edX/Open_DemoX/chapter/d8a6192ade314473a78242dfeedfbf5b')
        self.assertEqual(resolver.kwargs['page_id'], 'i4x://edX/Open_DemoX/sequential/edx_introduction')

    def test_navigate_to_page_url(self):
        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/overview')
        self.assertEqual(resolver.view_name, 'course_overview')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/announcements')
        self.assertEqual(resolver.view_name, 'course_news')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/resources')
        self.assertEqual(resolver.view_name, 'course_resources')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

class MockCourseAPI(object):

    @staticmethod
    def _get_course(course_id, force_course_id=0):
        course_dictionary = {
            "category": "course",
            "id": force_course_id,
            "name": "Test Course Name",
            "chapters": [
                {
                    "category": "chapter",
                    "id": "10",
                    "name": "Test Chapter 1",
                    "sequentials": [
                        {
                            "category": "sequential",
                            "id": "9100",
                            "name": "Test Sequential 1",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "100",
                                    "name": "Test Page 1",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1000",
                                            "name": "Test XBlock 1"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9101",
                            "name": "Test Sequential 2",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "101",
                                    "name": "Test Page 2",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1001",
                                            "name": "Test XBlock 2"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9102",
                            "name": "Test Sequential 3",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "102",
                                    "name": "Test Page 3",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1002",
                                            "name": "Test XBlock 3"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9103",
                            "name": "Test Sequential 4",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "103",
                                    "name": "Test Page 4",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1003",
                                            "name": "Test XBlock 4"
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                },
                {
                    "category": "chapter",
                    "id": "11",
                    "name": "Test Chapter 2",
                    "sequentials": [
                        {
                            "category": "sequential",
                            "id": "9110",
                            "name": "Test Sequential 1",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "110",
                                    "name": "Test Page 1",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1010",
                                            "name": "Test XBlock 1"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9111",
                            "name": "Test Sequential 2",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "111",
                                    "name": "Test Page 2",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1011",
                                            "name": "Test XBlock 2"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9112",
                            "name": "Test Sequential 3",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "112",
                                    "name": "Test Page 3",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1012",
                                            "name": "Test XBlock 3"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9113",
                            "name": "Test Sequential 4",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "113",
                                    "name": "Test Page 4",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1013",
                                            "name": "Test XBlock 4"
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                },
                {
                    "category": "chapter",
                    "id": "12",
                    "name": "Test Chapter 3",
                    "sequentials": [
                        {
                            "category": "sequential",
                            "id": "9120",
                            "name": "Test Sequential 1",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "120",
                                    "name": "Test Page 1",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1020",
                                            "name": "Test XBlock 1"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9121",
                            "name": "Test Sequential 2",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "121",
                                    "name": "Test Page 2",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1021",
                                            "name": "Test XBlock 2"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9122",
                            "name": "Test Sequential 3",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "122",
                                    "name": "Test Page 3",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1022",
                                            "name": "Test XBlock 3"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "category": "sequential",
                            "id": "9123",
                            "name": "Test Sequential 4",
                            "pages":[
                                {
                                    "category": "vertical",
                                    "id": "123",
                                    "name": "Test Page 4",
                                    "children":[
                                        {
                                            "category": "xblock",
                                            "id": "1023",
                                            "name": "Test XBlock 4"
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                },
            ]
        }

        return course_models.Course(dictionary=course_dictionary)

    @staticmethod
    def get_course(course_id, depth = 3, user=None):
        return MockCourseAPI._get_course(course_id, 0)

    @staticmethod
    def _get_course_navigation(course_id, target_location_id):
        response = None
        course = MockCourseAPI.get_course(course_id)
        for chapter in course.chapters:
            for section in chapter.sequentials:
                for vertical in section.pages:
                    for child in vertical.children:
                        if child.id == target_location_id:
                            response = {
                                "category": "course",
                                "id": course_id,
                                "name": "Test Course Name",
                                'course_key': '0',
                                'chapter': chapter.id,
                                'section': section.id,
                                'vertical': vertical.id,
                                'position': '0',
                                'final_target_id': child.id
                            }
        if response:
            return course_models.Course(dictionary=response)
        else:
            return None

    @staticmethod
    def get_course_navigation(course_id, target_location_id):
        return MockCourseAPI._get_course_navigation(course_id, target_location_id)


class OtherMockCourseAPI(MockCourseAPI):

    @staticmethod
    def get_course(course_id, depth = 3, user=None):
        return OtherMockCourseAPI._get_course(course_id, course_id)

class MockUserAPI(object):

    @staticmethod
    def _get_user_courses(user_id, current_course_id):
        users_courses = [
            {
                "id": current_course_id,
                "name": "Cycling to Work",
                "is_active": True
            },
            {
                "id": "1",
                "name": "Walking",
                "is_active": True
            },
            {
                "id": "3",
                "name": "Trains and Buses",
                "is_active": True
            },
            {
                "id": "4",
                "name": "Drive Yourself",
                "is_active": True,
                "start_date": "2014-06-01T00:14:00.00Z"
            }
        ]

        return [course_models.Course(dictionary=course) for course in users_courses]

    @staticmethod
    def get_user_courses(user_id):
        return MockUserAPI._get_user_courses(user_id, "2")

    @staticmethod
    def get_user_course_detail(user_id, course_id):
        course_detail = {
            "course_id": course_id,
            "position": 2,
            "user_id": user_id,
            "uri": "/api/users/{}/courses/{}".format(user_id, course_id)
        }
        return user_models.UserCourseStatus(dictionary=course_detail)

    @staticmethod
    def get_user_preferences(user_id):
        return {
            "current_course_id": "2",
            "last_chapter_id": "11",
            "last_sequential_id": "9111",
            "last_vertical_id": "111",
        }

    @staticmethod
    def set_user_preferences(user_id, prefs):
        pass

class NotBookmarkedMockUserAPI(MockUserAPI):

    @staticmethod
    def get_user_courses(user_id):
        return NotBookmarkedMockUserAPI._get_user_courses(user_id, "0")

# Create your tests here.

class CoursesAPITest(TestCase):

    def setUp(self):
        pass

    def test_build_page_info_for_course(self):
        test_course = controller.build_page_info_for_course(None, "0", "11", "112", MockCourseAPI)

        self.assertEqual(len(test_course.chapters), 3)
        self.assertEqual(test_course.current_lesson.id, "11")
        self.assertEqual(test_course.current_lesson.name, "Test Chapter 2")
        self.assertEqual(test_course.current_module.id, "112")
        self.assertEqual(test_course.current_module.name, "Test Page 3")

        for x in range(0, 3):
            self.assertEqual(test_course.chapters[x].navigation_url, "/courses/0/lessons/{}".format(10 + x))
            # print test_course.chapters[x].navigation_url
            for y in range(0, 4):
                self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].navigation_url, "/courses/0/lessons/{}/module/{}".format(10 + x, 100 + (x * 10) + y))
                if x == 1:
                    self.assertEqual(test_course.chapters[x].previous_module.navigation_url, "/courses/0/lessons/{}/module/{}".format(10 + x, 111))
                    self.assertEqual(test_course.chapters[x].next_module.navigation_url, "/courses/0/lessons/{}/module/{}".format(10 + x, 113))
                else:
                    self.assertEqual(hasattr(test_course.chapters[x], 'previous_module'), False)
                    self.assertEqual(hasattr(test_course.chapters[x], 'next_module'), False)

                #print "x = {}; y = {}; nav_url = {}; prev_url = {}; next_url = {}".format(x, y, test_course.chapters[x].pages[y].navigation_url, test_course.chapters[x].pages[y].prev_url, test_course.chapters[x].pages[y].next_url)

    def test_locate_chapter_page(self):
        # specified up to chapter id, should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page(None, "0", "2", "10", MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

        # specified course-only should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page(None, "0", "2", None, MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")

        # specified up to chapter id not bookmarked should get first page in specified chapter
        course_id, chapter_id, page_id = controller.locate_chapter_page(None, "0", "2", "12", NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "12")
        self.assertEqual(page_id, "120")

        # specified course-only without bookmark should get first page of first chapter
        course_id, chapter_id, page_id = controller.locate_chapter_page(None, "0", "0", None, NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "0")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

        # specified course-only without bookmark should get first page of first
        # chapter of specified course, even if "current" course is something
        # different
        course_id, chapter_id, page_id = controller.locate_chapter_page(None, "0", "9", None, NotBookmarkedMockUserAPI, OtherMockCourseAPI)

        self.assertEqual(course_id, "9")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")


    def test_get_chapter_and_target_by_location(self):
        def _get_chapter(course_id, location_id):
            chapter, sequential, page = controller.get_chapter_and_target_by_location(
                None, course_id, location_id, MockCourseAPI
            )
            return chapter, sequential, page

        self.assertEqual(_get_chapter("0", "1000"), ('10', '100', '1000'))
        self.assertEqual(_get_chapter("0", "1002"), ('10', '102', '1002'))
        self.assertEqual(_get_chapter("0", "1010"), ('11', '110', '1010'))
        self.assertEqual(_get_chapter("0", "1013"), ('11', '113', '1013'))
        self.assertEqual(_get_chapter("0", "1021"), ('12', '121', '1021'))
        self.assertEqual(_get_chapter("0", "1023"), ('12', '123', '1023'))
        self.assertEqual(_get_chapter("0", "150"), (None, None, None))
        self.assertEqual(_get_chapter("0", "I'm page"), (None, None, None))
        self.assertEqual(_get_chapter("0", "I'm page too"), (None, None, None))


class InferPageNavigationTests(TestCase):
    def _make_patch(self, target, new_value=None):
        new_val = new_value \
            if new_value else mock.Mock()
        patcher = mock.patch(target, new_val)
        patched =patcher.start()

        self.addCleanup(patcher.stop)
        return patched

    def _get_request_mock(self, user_id, course_id):
        request_mock = mock.Mock()
        request_mock.user.id = user_id

        course_mock = mock.Mock()
        course_mock.id = course_id
        course_mock.started = True
        program_mock = mock.Mock()
        program_mock.courses = [course_mock]

        # needed to pass check_user_course_access decorator
        request_mock.session = {CURRENT_PROGRAM: program_mock}
        return request_mock

    def setUp(self):

        self.load_course_mock = self._make_patch('courses.views.load_course')
        self.user_api_mock = self._make_patch('courses.views.user_api')
        self.get_group_project_for_user_course_mock = \
            self._make_patch('courses.views.get_group_project_for_user_course')
        self.get_group_project_for_user_course_mock.return_value = (None, None)

        self.get_chapter_and_target_by_location_mock = \
            self._make_patch('courses.views.get_chapter_and_target_by_location')
        self.get_chapter_and_target_by_location_mock.return_value = ('chapter_id', 'vertical_id', 'final_target_id')

    def test_infer_page_navigation_no_group_work_does_not_crash(self):
        request = self._get_request_mock(1, 'course_id')
        self.get_group_project_for_user_course_mock.return_value = (None, None)

        try:
            infer_page_navigation(request, 'course_id', 'page_id')
        except Exception as exc:
            self.fail("infer_page_navigation raised exception {exception} unexpectedly\n{traceback}".format(
                exception=exc, traceback=traceback.format_exc()
            ))
