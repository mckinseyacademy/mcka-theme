from django.test import TestCase
from api_client import course_models, user_models
from django.core.urlresolvers import resolve

from . import controller

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name

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
                                    "name": "Test Page 1"
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
                                    "name": "Test Page 2"
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
                                    "name": "Test Page 3"
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
                                    "name": "Test Page 4"
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
                                    "name": "Test Page 1"
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
                                    "name": "Test Page 2"
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
                                    "name": "Test Page 3"
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
                                    "name": "Test Page 4"
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
                                    "name": "Test Page 1"
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
                                    "name": "Test Page 2"
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
                                    "name": "Test Page 3"
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
                                    "name": "Test Page 4"
                                }
                            ]
                        },
                    ]
                },
            ]
        }

        return course_models.Course(dictionary=course_dictionary)

    @staticmethod
    def get_course(course_id, depth = 3):
        return MockCourseAPI._get_course(course_id, 0)

class OtherMockCourseAPI(MockCourseAPI):

    @staticmethod
    def get_course(course_id, depth = 3):
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
