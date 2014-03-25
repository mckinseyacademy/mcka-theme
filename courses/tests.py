from django.test import TestCase
from api_client import course_models, user_models

import controller

class MockCourseAPI(object):
    
    @staticmethod
    def _get_course(course_id, force_course_id = 0):
        course_dictionary =  {
            "course_id": force_course_id,
            "course_name": "Test Course Name",
            "chapters":[
                {
                    "chapter_id": 10,
                    "chapter_name": "Test Chapter 1",
                    "pages": [
                        {
                            "page_id": 100,
                            "page_name": "Test Page 1",
                        },
                        {
                            "page_id": 101,
                            "page_name": "Test Page 2",
                        },
                        {
                            "page_id": 102,
                            "page_name": "Test Page 3",
                        },
                        {
                            "page_id": 103,
                            "page_name": "Test Page 4",
                        },
                    ]
                },
                {
                    "chapter_id": 11,
                    "chapter_name": "Test Chapter 2",
                    "pages": [
                        {
                            "page_id": 110,
                            "page_name": "Test Page 1",
                        },
                        {
                            "page_id": 111,
                            "page_name": "Test Page 2",
                        },
                        {
                            "page_id": 112,
                            "page_name": "Test Page 3",
                        },
                        {
                            "page_id": 113,
                            "page_name": "Test Page 4",
                        },
                    ]
                },
                {
                    "chapter_id": 12,
                    "chapter_name": "Test Chapter 3",
                    "pages": [
                        {
                            "page_id": 120,
                            "page_name": "Test Page 1",
                        },
                        {
                            "page_id": 121,
                            "page_name": "Test Page 2",
                        },
                        {
                            "page_id": 122,
                            "page_name": "Test Page 3",
                        },
                        {
                            "page_id": 123,
                            "page_name": "Test Page 4",
                        },
                    ]
                },
            ]
        }

        return course_models.Course(dictionary=course_dictionary)

    @staticmethod
    def get_page_content(page_content_id):
        raise NotImplementedError

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
            "current_course_id": current_course_id,
            "courses": 
            [
                {
                    "course_id": 1,
                    "percent_complete": 100
                },
                {
                    "course_id": 2,
                    "percent_complete": 40,
                    "bookmark": 
                        {
                            "chapter_id": 10,
                            "page_id": 101
                        }
                },
                {
                    "course_id": 3,
                    "percent_complete": 10,
                    "bookmark": 
                        {
                            "chapter_id": 11,
                            "page_id": 111
                        }
                },
                {
                    "course_id": 4,
                    "percent_complete": 0,
                    "start_date": "2014-05-01T00:14:00.00Z"
                }
            ]
        }
        return user_models.UserStatus(dictionary=user_status_dictionary)

    @staticmethod
    def get_user_course_status(user_id):
        return MockUserAPI._get_user_course_status(user_id, 2)


class NotBookmarkedMockUserAPI(MockUserAPI):
    @staticmethod
    def get_user_course_status(user_id):
        return NotBookmarkedMockUserAPI._get_user_course_status(user_id, 0)

# Create your tests here.
class CoursesAPITest(TestCase):

    def setUp(self):
        pass

    def test_is_int_equal(self):
        for x in [1,100]:
            self.assertEqual(x,x)
            self.assertTrue(controller._is_int_equal(x,x))
            y = str(x)
            self.assertTrue(controller._is_int_equal(y,x))
            self.assertTrue(controller._is_int_equal(x,y))

    def test_build_page_info_for_course(self):
        test_course, test_current_chapter, test_current_page = controller.build_page_info_for_course(0, 11, 112, MockCourseAPI)
        
        self.assertEqual(len(test_course.chapters), 3)
        self.assertEqual(test_current_chapter.chapter_id, 11)
        self.assertEqual(test_current_chapter.chapter_name, "Test Chapter 2")
        self.assertEqual(test_current_page.page_id, 112)
        self.assertEqual(test_current_page.page_name, "Test Page 3")

        prev_url = None
        for x in [0,2]:
            test_course.chapters[0].navigation_url, "/courses/0/lessons/{}".format(10+x)
            for y in [0,3]:
                test_course.chapters[0].pages[y].navigation_url, "/courses/0/lessons/{}/modules/{}".format(10 + x, 100 + (x * 10) + y)
                test_course.chapters[0].pages[y].prev_url, prev_url
                if x == 2 and y == 3:
                    test_course.chapters[0].pages[y].next_url, None
                elif y == 3:    
                    test_course.chapters[0].pages[y].next_url, "/courses/0/lessons/{}/modules/{}".format(10 + x + 1, 100 + ((x+1) * 10))
                else:
                    test_course.chapters[0].pages[y].next_url, "/courses/0/lessons/{}/modules/{}".format(10 + x, 100 + (x * 10) + y + 1)
                prev_url = test_course.chapters[0].pages[y].navigation_url

    def test_locate_chapter_page(self):
        # specified up to chapter id, should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, 2, 10, MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, 2)
        self.assertEqual(chapter_id, 10)
        self.assertEqual(page_id, 101)

        # specified course-only should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, 2, None, MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, 2)
        self.assertEqual(chapter_id, 10)
        self.assertEqual(page_id, 101)

        # specified user-only should get bookmarked page
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, None, None, MockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, 2)
        self.assertEqual(chapter_id, 10)
        self.assertEqual(page_id, 101)

        # specified up to chapter id not bookmarked should get first page in specified chapter
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, 0, 11, NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, 0)
        self.assertEqual(chapter_id, 11)
        self.assertEqual(page_id, 110)

        # specified course-only without bookmark should get first page of first chapter
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, 0, None, NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, 0)
        self.assertEqual(chapter_id, 10)
        self.assertEqual(page_id, 100)

        # specified course-only without bookmark should get first page of first chapter of specified course, even if "current" course is something different
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, 9, None, NotBookmarkedMockUserAPI, OtherMockCourseAPI)

        self.assertEqual(course_id, 9)
        self.assertEqual(chapter_id, 10)
        self.assertEqual(page_id, 100)

        # specified user-only should get first page of first chapter too
        course_id, chapter_id, page_id = controller.locate_chapter_page(0, None, None, NotBookmarkedMockUserAPI, MockCourseAPI)

        self.assertEqual(course_id, 0)
        self.assertEqual(chapter_id, 10)
        self.assertEqual(page_id, 100)


