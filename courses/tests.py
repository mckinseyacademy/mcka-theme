from django.test import TestCase
from api_client import course_models, user_models
from django.core.urlresolvers import resolve

from . import controller

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name


class UrlsTest(TestCase):

    def test_infer_course_navigation_url(self):
        resolver = resolve('/courses/c152')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')

        resolver = resolve('/courses/ABC/123/456/789')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course')
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

    def test_navigate_to_page_url(self):
        resolver = resolve('/courses/c152/lessons/ch153/module/p154')
        self.assertEqual(resolver.view_name, 'navigate_to_page')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['chapter_id'], 'ch153')
        self.assertEqual(resolver.kwargs['page_id'], 'p154')

        resolver = resolve('/courses/ABC/123/456/789/lessons/XYZ/987/654/321/module/LMN/ZXC/LAKSJDFLASKJFLWE/444')
        self.assertEqual(resolver.view_name, 'navigate_to_page')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['chapter_id'], 'XYZ/987/654/321')
        self.assertEqual(resolver.kwargs['page_id'], 'LMN/ZXC/LAKSJDFLASKJFLWE/444')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons/i4x://edX/Open_DemoX/chapter/d8a6192ade314473a78242dfeedfbf5b/module/i4x://edX/Open_DemoX/sequential/edx_introduction')
        self.assertEqual(resolver.view_name, 'navigate_to_page')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['chapter_id'], 'i4x://edX/Open_DemoX/chapter/d8a6192ade314473a78242dfeedfbf5b')
        self.assertEqual(resolver.kwargs['page_id'], 'i4x://edX/Open_DemoX/sequential/edx_introduction')


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
    def get_course(course_id):
        return MockCourseAPI._get_course(course_id, 0)


class OtherMockCourseAPI(MockCourseAPI):

    @staticmethod
    def get_course(course_id):
        return OtherMockCourseAPI._get_course(course_id, course_id)


class MockUserAPI(object):

    @staticmethod
    def _get_user_course_status(user_id, current_course_id):
        user_status_dictionary = {
            "current_program_id": "1001",
            "current_course_id": current_course_id,
            "programs":
                [
                    {
                        "id": "1001",
                        "name": "Different Transportation Methods",
                        "courses":
                        [
                            {"id":"1"},
                            {"id":"2"},
                            {"id":"3"},
                            {"id":"4"}
                        ]
                    }
                ],
            "courses":
                [
                    {
                        "id": "1",
                        "name": "Walking",
                        "percent_complete": 100
                    },
                    {
                        "id": "2",
                        "name": "Cycling to Work",
                        "percent_complete": 40,
                        "bookmark":
                            {
                                "chapter_id": "10",
                                "page_id": "101"
                            }
                    },
                    {
                        "id": "3",
                        "name": "Trains and Buses",
                        "percent_complete": 10,
                        "bookmark":
                            {
                                "chapter_id": "10",
                                "page_id": "101"
                            }
                    },
                    {
                        "id": "4",
                        "name": "Drive Yourself",
                        "percent_complete": 0,
                        "start_date": "2014-06-01T00:14:00.00Z"
                    }
                ]
        }

        return user_models.UserStatus(dictionary=user_status_dictionary)

    @staticmethod
    def get_user_course_status(user_id):
        return MockUserAPI._get_user_course_status(user_id, "2")


class NotBookmarkedMockUserAPI(MockUserAPI):

    @staticmethod
    def get_user_course_status(user_id):
        return NotBookmarkedMockUserAPI._get_user_course_status(user_id, "0")

# Create your tests here.


class CoursesAPITest(TestCase):

    def setUp(self):
        pass

    def test_build_page_info_for_course(self):
        test_course, test_current_chapter, test_current_sequential, test_current_page = controller.build_page_info_for_course("0", "11", "112", MockCourseAPI)

        self.assertEqual(len(test_course.chapters), 3)
        self.assertEqual(test_current_chapter.id, "11")
        self.assertEqual(test_current_chapter.name, "Test Chapter 2")
        self.assertEqual(test_current_page.id, "112")
        self.assertEqual(test_current_page.name, "Test Page 3")

        prev_url = None
        for x in range(0, 3):
            self.assertEqual(test_course.chapters[x].navigation_url, "/courses/0/lessons/{}".format(10 + x))
            # print test_course.chapters[x].navigation_url
            for y in range(0, 4):
                self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].navigation_url, "/courses/0/lessons/{}/module/{}".format(10 + x, 100 + (x * 10) + y))
                self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].prev_url, prev_url)
                if x == 2 and y == 3:
                    self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].next_url, None)
                elif y == 3:
                    self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].next_url, "/courses/0/lessons/{}/module/{}".format(10 + x + 1, 100 + ((x + 1) * 10)))
                else:
                    self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].next_url, "/courses/0/lessons/{}/module/{}".format(10 + x, 100 + (x * 10) + y + 1))
                prev_url = test_course.chapters[x].sequentials[y].pages[0].navigation_url

                #print "x = {}; y = {}; nav_url = {}; prev_url = {}; next_url = {}".format(x, y, test_course.chapters[x].pages[y].navigation_url, test_course.chapters[x].pages[y].prev_url, test_course.chapters[x].pages[y].next_url)


    def test_locate_chapter_page(self):
        # specified up to chapter id, should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", "2", "10", MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "101")

        # specified course-only should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", "2", None, MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "101")

        # specified user-only should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", None, None, MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "101")

        # specified up to chapter id not bookmarked should get first page in specified chapter
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", "0", "11", NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "0")
        self.assertEqual(chapter_id, "11")
        self.assertEqual(page_id, "110")

        # specified course-only without bookmark should get first page of first chapter
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", "0", None, NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "0")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

        # specified course-only without bookmark should get first page of first
        # chapter of specified course, even if "current" course is something
        # different
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", "9", None, NotBookmarkedMockUserAPI, OtherMockCourseAPI)

        self.assertEqual(course_id, "9")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

        # specified user-only should get first page of first chapter too
        course_id, chapter_id, page_id = controller.locate_chapter_page("0", None, None, NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, "0")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

    def test_program_for_course(self):
        # course within a program
        test_program = controller.program_for_course("0", "2", MockUserAPI)
        self.assertEqual(test_program.id, "1001")
        self.assertEqual(test_program.name, "Different Transportation Methods")

        self.assertEqual(len(test_program.courses), 4)

        # course not within a program
        test_program = controller.program_for_course("0", "5", MockUserAPI)
        self.assertEqual(test_program, None)
