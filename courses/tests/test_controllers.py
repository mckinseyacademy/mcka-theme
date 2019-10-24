import json

import ddt
import mock
import httpretty
from bs4 import BeautifulSoup
from django.conf import settings
from django.test import TestCase, override_settings, Client

from admin.models import LearnerDashboard, LearnerDashboardTile, LearnerDashboardTileProgress
from admin.forms import LearnerDashboardTileForm
from api_client import course_api, course_models, user_models
from api_client.user_api import USER_API
from api_client.api_error import ApiError
from lib.utils import DottableDict
from courses.models import FeatureFlags
from courses.controller import (
    build_page_info_for_course,
    locate_chapter_page,
    get_group_project_for_user_course,
    get_group_project_for_workgroup_course,
    group_project_location,
    group_project_reviews,
    get_chapter_and_target_by_location,
    get_completion_percentage_from_id,
    organization_course_progress_user_list,
    return_course_progress,
    average_progress,
    get_proficiency_leaders,
    get_progress_leaders,
    social_total,
    get_course_social_metrics,
    get_user_social_metrics,
    get_social_leaders,
    get_leaders,
    progress_update_handler,
    get_course_object,
    createProgressObjects,
    choose_random_ta,
    fix_resource_page_video_scripts,
    _remove_duplicate_grader,
    get_non_staff_user,
    user_learner_dashboards,
    get_learner_dashboard
)

from util.unit_test_helpers.test_api_responses import (
    course_metrics as test_course_metrics_data,
    course as test_course_data,
    user as test_user_data,
    project as test_project_data,
    workgroup as test_workgroup_data,
)
from util.unit_test_helpers.common_mocked_objects import TestUser, ApplyPatchMixin


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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "100",
                                    "name": "Test Page 1",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1000",
                                            "name": "Test XBlock 1"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "100",
                                    "name": "Test Page 1",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "101",
                                    "name": "Test Page 2",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1001",
                                            "name": "Test XBlock 2"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "101",
                                    "name": "Test Page 2",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "102",
                                    "name": "Test Page 3",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1002",
                                            "name": "Test XBlock 3"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "102",
                                    "name": "Test Page 3",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "103",
                                    "name": "Test Page 4",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1003",
                                            "name": "Test XBlock 4"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "103",
                                    "name": "Test Page 4",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "110",
                                    "name": "Test Page 1",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1010",
                                            "name": "Test XBlock 1"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "110",
                                    "name": "Test Page 1",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "111",
                                    "name": "Test Page 2",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1011",
                                            "name": "Test XBlock 2"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "111",
                                    "name": "Test Page 2",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "112",
                                    "name": "Test Page 3",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1012",
                                            "name": "Test XBlock 3"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "112",
                                    "name": "Test Page 3",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "113",
                                    "name": "Test Page 4",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1013",
                                            "name": "Test XBlock 4"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "113",
                                    "name": "Test Page 4",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "120",
                                    "name": "Test Page 1",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1020",
                                            "name": "Test XBlock 1"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "120",
                                    "name": "Test Page 1",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "121",
                                    "name": "Test Page 2",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1021",
                                            "name": "Test XBlock 2"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "121",
                                    "name": "Test Page 2",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "122",
                                    "name": "Test Page 3",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1022",
                                            "name": "Test XBlock 3"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "122",
                                    "name": "Test Page 3",
                                    "children": [
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
                            "children": [
                                {
                                    "category": "vertical",
                                    "id": "123",
                                    "name": "Test Page 4",
                                    "children": [
                                        {
                                            "category": "xblock",
                                            "id": "1023",
                                            "name": "Test XBlock 4"
                                        }
                                    ]
                                }
                            ],
                            "pages": [
                                {
                                    "category": "vertical",
                                    "id": "123",
                                    "name": "Test Page 4",
                                    "children": [
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
    def get_course(course_id, depth=3, user=None):
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


class OtherMockCourseAPI(MockCourseAPI):
    @staticmethod
    def get_course(course_id, depth=3, user=None):
        return OtherMockCourseAPI._get_course(course_id, course_id)


@ddt.ddt
class CoursesAPITest(TestCase):
    def test_build_page_info_for_course(self):
        test_course = build_page_info_for_course(None, "0", "11", "112", MockCourseAPI)

        self.assertEqual(len(test_course.chapters), 3)
        self.assertEqual(test_course.current_lesson.id, "11")
        self.assertEqual(test_course.current_lesson.name, "Test Chapter 2")
        self.assertEqual(test_course.current_module.id, "112")
        self.assertEqual(test_course.current_module.name, "Test Page 3")

        for x in range(0, 3):
            self.assertEqual(test_course.chapters[x].navigation_url, "/courses/0/lessons/{}".format(10 + x))
            # print test_course.chapters[x].navigation_url
            for y in range(0, 4):
                self.assertEqual(test_course.chapters[x].sequentials[y].pages[0].navigation_url,
                                 "/courses/0/lessons/{}/module/{}".format(10 + x, 100 + (x * 10) + y))
                if x == 1:
                    self.assertEqual(test_course.chapters[x].previous_module.navigation_url,
                                     "/courses/0/lessons/{}/module/{}".format(10 + x, 111))
                    self.assertEqual(test_course.chapters[x].next_module.navigation_url,
                                     "/courses/0/lessons/{}/module/{}".format(10 + x, 113))
                else:
                    self.assertEqual(hasattr(test_course.chapters[x], 'previous_module'), False)
                    self.assertEqual(hasattr(test_course.chapters[x], 'next_module'), False)

    def test_locate_chapter_page(self):
        # specified up to chapter id, should get bookmarked page
        course_id, chapter_id, page_id = locate_chapter_page(None, "0", "2", "10", MockUserAPI,
                                                                        MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

        # specified course-only should get bookmarked page
        course_id, chapter_id, page_id = locate_chapter_page(None, "0", "2", None, MockUserAPI,
                                                                        MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "10")

        # specified up to chapter id not bookmarked should get first page in specified chapter
        course_id, chapter_id, page_id = locate_chapter_page(None, "0", "2", "12", NotBookmarkedMockUserAPI,
                                                                        MockCourseAPI)

        self.assertEqual(course_id, "2")
        self.assertEqual(chapter_id, "12")
        self.assertEqual(page_id, "120")

        # specified course-only without bookmark should get first page of first chapter
        course_id, chapter_id, page_id = locate_chapter_page(None, "0", "0", None, NotBookmarkedMockUserAPI,
                                                                        MockCourseAPI)

        self.assertEqual(course_id, "0")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

        # specified course-only without bookmark should get first page of first
        # chapter of specified course, even if "current" course is something
        # different
        course_id, chapter_id, page_id = locate_chapter_page(None, "0", "9", None, NotBookmarkedMockUserAPI,
                                                                        OtherMockCourseAPI)

        self.assertEqual(course_id, "9")
        self.assertEqual(chapter_id, "10")
        self.assertEqual(page_id, "100")

    def test_get_chapter_and_target_by_location(self):
        def _get_chapter(course_id, location_id):
            chapter, sequential, page = get_chapter_and_target_by_location(
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

    def test_get_completion_percentage_from_id(self):
        data = {
            'completion': {
                'earned': 12.0,
                'possible': 24.0,
                'percent': 0.5,
            },
            'chapter': [
                {
                    'course_key': 'a/b/c',
                    'block_key': 'i4x://a/b/chapter/chapter-1',
                    'completion': {
                        'earned': 6.0,
                        'possible': 8.0,
                        'percent': 0.75,
                    }
                },
                {
                    'course_key': 'a/b/c',
                    'block_key': 'i4x://a/b/chapter/chapter-2',
                    'completion': {
                        'earned': 6.0,
                        'possible': 12.0,
                        'percent': 0.5,
                    }
                },
                {
                    'course_key': 'a/b/c',
                    'block_key': 'i4x://a/b/chapter/chapter-3',
                    'completion': {
                        'earned': 0.0,
                        'possible': 2.0,
                        'percent': 0.0,
                    }
                },
                {
                    'course_key': 'a/b/c',
                    'block_key': 'i4x://a/b/chapter/chapter-4',
                    'completion': {
                        'earned': 0.0,
                        'possible': None,
                        'percent': None,
                    }
                },
            ]
        }

        completions = course_api.group_completions_by_user([data], 'ali')['ali']
        get_completions = get_completion_percentage_from_id
        self.assertEqual(get_completions(completions, 'course'), 50)
        self.assertEqual(get_completions(completions, 'chapter', 'i4x://a/b/chapter/chapter-1'), 75)
        self.assertEqual(get_completions(completions, 'chapter', 'i4x://a/b/chapter/chapter-2'), 50)
        self.assertEqual(get_completions(completions, 'chapter', 'i4x://a/b/chapter/chapter-3'), 0)
        self.assertEqual(get_completions(completions, 'chapter', 'i4x://a/b/chapter/chapter-4'), 0)
        self.assertEqual(get_completions(completions, 'chapter', 'i4x://a/b/chapter/chapter-5'), 0)

    @staticmethod
    def _setup_user_social_metrics_response(user_id, course_id, include_stats, throw_error):
        response_data = {
            'score': 11,
            'course_avg': 8.7,
        }
        if include_stats:
            response_data['stats'] = {
                'num_threads': 4,
                'num_thread_followers': 3,
                'num_replies': 11,
                'num_flagged': 0,
                'num_comments': 22,
                'num_threads_read': 131,
                'num_downvotes': 2,
                'num_upvotes': 6,
                'num_comments_generated': 40
            }
        httpretty.register_uri(
            httpretty.GET,
            '{}/{}/{}/courses/{}/metrics/social/?{}'.format(
                settings.API_SERVER_ADDRESS,
                USER_API,
                user_id,
                course_id,
                'include_stats=true' if include_stats else ''
            ),
            # match_querystring=False,
            body=json.dumps(response_data),
            status=444 if throw_error else 200,
            content_type='application/json'
        )

    @httpretty.httprettified
    def test_get_course_social_metrics(self):
        course_id = 'some/course/id'
        test_course_metrics_data.setup_get_course_social_metrics_response(course_id)

        course_social_metrics = get_course_social_metrics(course_id)
        self.assertEqual(course_social_metrics.total_enrollments, 4)
        for u_id, user_metrics in course_social_metrics.users.__dict__.items():
            self.assertEqual(vars(user_metrics), test_course_metrics_data.course_social_metrics['users'][str(u_id)])

    @ddt.data(
        # Throw error, response metrics
        (False, 11, 9, 4, 131),
        (True, 0, 0, 0, 0),
    )
    @ddt.unpack
    @httpretty.httprettified
    def test_get_user_social_metrics_with_stats(self, throw_error, score, average, threads, threads_read):
        user_id = 1
        course_id = 'some/course/id'
        self._setup_user_social_metrics_response(user_id, course_id, True, throw_error)
        data = get_user_social_metrics(user_id, course_id, include_stats=True)
        self.assertEqual(data['points'], score)
        self.assertEqual(data['course_avg'], average)
        self.assertEqual(data['metrics'].num_threads, threads)
        self.assertEqual(data['metrics'].num_threads_read, threads_read)

    @ddt.data(
        # Throw error, response metrics
        (False, 11, 9),
        (True, 0, 0),
    )
    @ddt.unpack
    @httpretty.httprettified
    def test_get_user_social_metrics_without_stats(self, throw_error, score, average):
        user_id = 1
        course_id = 'some/course/id'
        self._setup_user_social_metrics_response(user_id, course_id, False, throw_error)
        data = get_user_social_metrics(user_id, course_id, include_stats=False)
        self.assertEqual(data['points'], score)
        self.assertEqual(data['course_avg'], average)
        self.assertIsNone(data['metrics'])

    @httpretty.activate
    def test_organization_course_progress_user_list(self):
        organization_id = 1
        course_id = 'some/course/id'
        test_course_metrics_data.setup_course_metrics_completions(course_id, organizations=organization_id)
        leaders = organization_course_progress_user_list(course_id, organization_id)

        course_metrics_completions_leaders_list = \
            test_course_metrics_data.course_metrics_completions_leaders_list['leaders']
        for l1, l2 in zip(leaders, course_metrics_completions_leaders_list):
            self.assertEqual(l1.id, l2['id'])
            self.assertEqual(l1.username, l2['username'])
            self.assertEqual(l1.title, l2['title'])
            self.assertEqual(l1.profile_image_uploaded_at, l2['profile_image_uploaded_at'])
            self.assertEqual(l1.completions, l2['completions'])

    @httpretty.activate
    def test_return_course_progress(self):
        user_id = 1
        self.course = MockCourseAPI._get_course('CS101/ORG101/2018', force_course_id='CS101/ORG101/2018')
        test_course_metrics_data.setup_course_metrics_completions(self.course.id, user_id=user_id, skipleaders=True)
        user_progress_display = return_course_progress(self.course, user_id)

        self.assertEqual(user_progress_display, 22)

    @httpretty.activate
    def test_average_progress(self):
        user_id = 1
        self.course = MockCourseAPI._get_course('CS101/ORG101/2018', force_course_id='CS101/ORG101/2018')
        test_course_metrics_data.setup_course_metrics_completions(self.course.id, user_id=user_id, skipleaders=True)
        course_average_display = average_progress(self.course, user_id)

        self.assertEqual(course_average_display, 7)

    @httpretty.activate
    def test_get_proficiency_leaders(self):
        user_id = 1
        course_id = 'some/course/id'
        count = 3
        test_course_metrics_data.setup_course_metrics_grades(course_id, count=count, user_id=user_id)
        proficiency = get_proficiency_leaders(course_id, user_id, count)

        course_metrics_grades_leaders_list = test_course_metrics_data.course_metrics_grades_leaders_list
        self.assertEqual(proficiency.course_avg, course_metrics_grades_leaders_list["course_avg"])
        self.assertEqual(len(proficiency.leaders), len(course_metrics_grades_leaders_list["leaders"]))
        self.assertEqual(proficiency.user_position, course_metrics_grades_leaders_list["user_position"])
        self.assertEqual(proficiency.user_grade, course_metrics_grades_leaders_list["user_grade"])

    @httpretty.activate
    def test_get_progress_leaders(self):
        user_id = 1
        course_id = 'some/course/id'
        test_course_metrics_data.setup_course_metrics_completions(course_id, user_id=user_id)
        completions = get_progress_leaders(course_id, user_id)

        course_metrics_completions_leaders_list = test_course_metrics_data.course_metrics_completions_leaders_list
        self.assertEqual(completions.completions, course_metrics_completions_leaders_list["completions"])
        self.assertEqual(completions.course_avg, course_metrics_completions_leaders_list["course_avg"])
        self.assertEqual(len(completions.leaders), len(course_metrics_completions_leaders_list["leaders"]))
        self.assertEqual(completions.position, course_metrics_completions_leaders_list["position"])
        self.assertEqual(completions.total_users, course_metrics_completions_leaders_list["total_users"])

    @ddt.data(
        # Throw error, response metrics
        (False, 22, 7, 4, 3),
        (True, 0, 0, 0, 0),
    )
    @ddt.unpack
    @httpretty.activate
    def test_get_social_leaders(self, throw_error, score, course_avg, position, leaders_length):
        user_id = 1
        course_id = 'some/course/id'
        count = 3
        test_course_metrics_data.setup_course_metrics_social(course_id, count, throw_error, user_id=user_id)
        data = get_social_leaders(course_id, user_id, count)
        self.assertEqual(data['points'], score)
        self.assertEqual(data['course_avg'], course_avg)
        self.assertEqual(data['position'], position)
        self.assertEqual(len(data['leaders']), leaders_length)

    @ddt.data(
        # Throw error, response data
        (False, test_course_metrics_data.course_metrics_leaders_data),
        (True, None),
    )
    @ddt.unpack
    @httpretty.activate
    def test_get_leaders(self, throw_error, course_metrics_leaders_data):
        user_id = 1
        course_id = 'some/course/id'
        count = 3
        test_course_metrics_data.setup_get_course_metrics_leaders_response(course_id=course_id, count=count,
                                                                           throw_error=throw_error, user_id=user_id)
        if not throw_error:
            data = get_leaders(course_id=course_id, user_id=user_id, count=count)
            self.assertEqual(len(data.grades.leaders), len(course_metrics_leaders_data["grades"]["leaders"]))
            self.assertEqual(len(data.completions.leaders), len(course_metrics_leaders_data["completions"]["leaders"]))
            self.assertEqual(len(data.social.leaders), len(course_metrics_leaders_data["social"]["leaders"]))
        else:
            with self.assertRaises(ApiError):
                get_leaders(course_id=course_id, user_id=user_id, count=count)


@ddt.ddt
class GroupProject(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.user = TestUser(user_id=1, email='mcka_admin_user@mckinseyacademy.com', username='mcka_admin_user')
        self.course = MockCourseAPI._get_course(
            'Organization_Y/CS105/2018_T5', force_course_id='Organization_Y/CS105/2018_T5'
        )
        self.course.group_projects = [DottableDict(group_project) for
                                      group_project in test_project_data.course_group_projects]

        self.url = "http://lms.mcka.local/api/server/projects/1/"
        get_project_url_by_id = self.apply_patch('courses.controller.project_api.get_project_url_by_id')
        get_project_url_by_id.return_value = self.url

        project_url_by_id = self.apply_patch('api_client.project_api.get_project_url_by_id')
        project_url_by_id.return_value = self.url

    def _assert_result(self, group_project, expected_group_project):
        self.assertEqual(group_project["id"], expected_group_project["id"])
        self.assertEqual(group_project["course_id"], expected_group_project["course_id"])
        self.assertEqual(group_project["name"], expected_group_project["name"])

        for index in range(len(group_project["activities"])):
            self.assertEqual(
                group_project["activities"][index]["id"], expected_group_project["activities"][index]["id"]
            )
            self.assertEqual(
                group_project["activities"][index]["name"], expected_group_project["activities"][index]["name"]
            )
            self.assertEqual(
                group_project["activities"][index]["link"], expected_group_project["activities"][index]["link"]
            )

    @ddt.data(
        2, None
    )
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    @httpretty.activate
    def test_get_group_project_for_user_course(self, workgroup_id):
        if workgroup_id:
            test_workgroup_data.setup_get_workgroup_response(2)

        test_user_data.setup_get_user_workgroups_response(self.user.id, self.course.id)
        test_workgroup_data.setup_get_workgroup_users_response(2)

        additional_fields = ["title", "first_name", "last_name", "profile_image"]
        test_user_data.setup_get_users_response(ids=['8', '9'], fields=additional_fields)
        test_project_data.setup_fetch_project_from_url_response(url=self.url)

        project_group, group_project = get_group_project_for_user_course(self.user.id, self.course, workgroup_id)

        self.assertEqual(project_group.id, 2)
        self.assertEqual(project_group.name, "Group 2")
        self.assertEqual(project_group.project, "http://lms.mcka.local/api/server/projects/1/")
        self.assertEqual(project_group.url, "http://lms.mcka.local/api/server/workgroups/2/")
        self.assertEqual(len(project_group.members), 2)

        self._assert_result(group_project, self.course.group_projects[0])

    @httpretty.activate
    def test_get_group_project_for_workgroup_course(self):
        workgroup_id = 2
        test_workgroup_data.setup_get_workgroup_response(workgroup_id)

        additional_fields = ["title", "first_name", "last_name", "profile_image"]
        test_user_data.setup_get_users_response(ids=['8', '9'], fields=additional_fields)
        test_project_data.setup_get_project_reponse(1)

        test_project_data.setup_fetch_project_from_url_response(url=self.url)

        workgroup, group_project = get_group_project_for_workgroup_course(workgroup_id, self.course)

        self.assertEqual(workgroup.id, 2)
        self.assertEqual(workgroup.name, "Group 2")
        self.assertEqual(workgroup.project, 1)
        self.assertEqual(workgroup.url, "http://lms.mcka.local/api/server/workgroups/2/")
        self.assertEqual(len(workgroup.members), 2)

        self._assert_result(group_project, self.course.group_projects[0])

    @ddt.data(
        True, False
    )
    @httpretty.activate
    def test_group_project_location(self, is_v2):
        group_project = test_project_data.course_group_projects[0]
        group_project["activities"] = [DottableDict(activity) for activity in group_project["activities"]]
        group_project["is_v2"] = is_v2

        if is_v2:
            activity, usage_id = group_project_location(DottableDict(group_project), sequential_id=None)
            self.assertEqual(activity, None)
            self.assertEqual(usage_id, 'i4x:;_;_Organization_Y;_CS105;_gp-v2-project;_1b4fc43f58a14705bb6c4f0e68f4cbaa')
        else:
            activity, usage_id = group_project_location(DottableDict(group_project), sequential_id=None)
            self.assertEqual(activity.category, 'gp-v2-activity')
            self.assertEqual(activity.name, 'Kickoff')
            self.assertEqual(activity.is_group_activity, True)
            self.assertEqual(
                activity.link, '/courses/Organization_Y/CS105/2018_T5/group_work?'
                               'activate_block_id=i4x%3A%2F%2FOrganization_Y%2FCS105%2Fgp-v2-activity%2'
                               'F2a4e4bb9b329420b84007d7e13f8a876'
            )
            self.assertEqual(
                activity.uri, 'http://lms.mcka.local/api/server/courses/Organization_Y/CS105/2018_T5/content/'
                              'i4x://Organization_Y/CS105/gp-v2-activity/2a4e4bb9b329420b84007d7e13f8a876'
            )
            self.assertEqual(activity.id, 'i4x://Organization_Y/CS105/gp-v2-activity/2a4e4bb9b329420b84007d7e13f8a876')
            self.assertEqual(
                usage_id, 'i4x:;_;_Organization_Y;_CS105;_gp-v2-activity;_2a4e4bb9b329420b84007d7e13f8a876'
            )

    def _assert_activities_result(self, activities, expected_activities):
        for activity, expected_activity in zip(activities, expected_activities):
            self.assertEqual(activity.category, expected_activity.category)
            self.assertEqual(activity.name, expected_activity.name)
            self.assertEqual(activity.is_group_activity, True)
            if activity.name == 'Kickoff':
                self.assertEqual(activity.pending_grades, [0])
                self.assertEqual(activity.grades, [80.0])
                self.assertEqual(activity.score, 80.0)
                self.assertEqual(activity.is_pending, True)
            elif activity.name == 'Strategy Table':
                self.assertEqual(activity.pending_grades, [])
                self.assertEqual(activity.grades, [80.0])
                self.assertEqual(activity.score, 80.0)
                self.assertEqual(activity.is_pending, False)
            elif activity.name == 'Ten Timeless Tests':
                self.assertEqual(activity.pending_grades, [])
                self.assertEqual(activity.grades, [])
                self.assertEqual(activity.score, None)
                self.assertEqual(activity.is_pending, False)

    @httpretty.activate
    def test_group_project_reviews(self):
        project_workgroup = mock.Mock()
        project_workgroup.id = 2

        group_project = test_project_data.course_group_projects[0]
        group_project["activities"] = [DottableDict(activity) for activity in group_project["activities"]]

        test_workgroup_data.setup_get_workgroup_review_items_response(project_workgroup.id)
        test_workgroup_data.setup_get_workgroup_groups_response(project_workgroup.id)
        test_workgroup_data.setup_get_users_in_group_response(2)

        activities, group_work_avg = group_project_reviews(
            self.user.id, self.course.id, project_workgroup, DottableDict(group_project)
        )

        self._assert_activities_result(activities, group_project["activities"])
        self.assertEqual(group_work_avg, 80.0)


@ddt.ddt
class ProgressUpdateHandlerTest(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.user = TestUser(user_id=1, email='mcka_admin_user@mckinseyacademy.com', username='mcka_admin_user')
        self.client = Client()

        self.course = MockCourseAPI._get_course('CS101/ORG101/2018', force_course_id='CS101/ORG101/2018')

        get_group_project_for_user_course = self.apply_patch('courses.controller.get_group_project_for_user_course')
        get_group_project_for_user_course.return_value = None, None

        self.learner_dashboard = LearnerDashboard(
            title='sample',
            description='sample tile',
            title_color='red',
            description_color='black',
            client_id=1,
            course_id='CS101/ORG101/2018'
        )
        self.learner_dashboard.save()

        element_types = {
            '1': '/courses/CS101/ORG101/2018/lessons/i4x://zeej/qa002/chapter/8fc3ceff802f40c8aea43cf2d58d8a28/'
                 'module/i4x://zeej/qa002/vertical/6150fcfeab4744f98ae4e39d76bcac5f',  # Article
            '2': '/learnerdashboard/courses/CS101/ORG101/2018/'
                 'lessons/i4x://zeeqa/qa003/chapter/7a97fd7dc5844534a739abd3f76fe77d/'
                 'module/i4x://zeeqa/qa003/vertical/cfdaa01f1920401fb3805d569fb8a6db/lesson/',  # Lesson
            '3': '/learnerdashboard/courses/CS101/ORG101/2018/'
                 'lessons/i4x://zeeqa/qa003/chapter/7a97fd7dc5844534a739abd3f76fe77d/'
                 'module/i4x://zeeqa/qa003/vertical/cfdaa01f1920401fb3805d569fb8a6db/module/',  # Module
            '4': '/courses/CS101/ORG101/2018',  # Course
            '5': '/learnerdashboard/courses/CS101/ORG101/2018/'
                 'lessons/i4x://zeeqa/qa003/chapter/7a97fd7dc5844534a739abd3f76fe77d/'
                 'module/i4x://zeeqa/qa003/vertical/cfdaa01f1920401fb3805d569fb8a6db/module/',  # In Person Session
            '6': '/courses/CS101/ORG101/2018/lessons/i4x://zeej/qa002/chapter/70765d4c023842f0a981216b17739441/module/'
                 'i4x://zeej/qa002/vertical/ad30881cc7474977b232cd91be5f68b3',  # Webinar
            '7': '/courses/CS101/ORG101/2018/group_work?'
                 'activate_block_id=i4x://DEV/SYN_LD/gp-v2-stage-basic/933ff6724fa54cad967ca9cde2d1844a'  # Group work
        }

        self.learner_dashboard_tile_form = {
            'track_progress': '',
            'label': 'sample label',
            'title': 'sample title',
            'note': 'sample note',
            'link': 'https://samplelink.com',
            'learner_dashboard': self.learner_dashboard.id,
            'label_color': 'red',
            'title_color': 'blue',
            'note_color': 'green',
            'tile_background_color': 'black',
            'download_link': 'https://samplelink.com',
            'publish_date': '',
            'background_image': '',
            'start_date': '',
            'end_date': '',
            'show_in_calendar': True,
            'show_in_dashboard': True,
            'hidden_from_learners': False,
            'fa_icon': '',
            'row': '1',
        }

        for key, val in list(element_types.items()):
            self.learner_dashboard_tile_form['tile_type'] = str(key)
            self.learner_dashboard_tile_form['link'] = str(val)
            form = LearnerDashboardTileForm(data=self.learner_dashboard_tile_form)
            form.save()

    @httpretty.activate
    def test_progress_update_handler(self):
        request = self.client.get(path='/')
        request.user = self.user

        test_course_metrics_data.setup_course_completions_response(self.course.id, username=request.user.username)
        test_course_data.setup_get_course_blocks_responses(
            self.course.id,
            depth='all',
            return_type='list',
            requested_fields='completion',
            username=request.user.username,
        )

        progress_update_handler(
            request,
            self.course,
            chapter_id="i4x://zeeqa/qa003/chapter/7a97fd7dc5844534a739abd3f76fe77d",
            page_id="i4x://zeeqa/qa003/vertical/cfdaa01f1920401fb3805d569fb8a6db"
        )
        learner_dashboard_tile_progress = LearnerDashboardTileProgress.objects.all()

        for tile_progress in learner_dashboard_tile_progress:
            if tile_progress.milestone.tile_type == '1':
                self.assertEqual(tile_progress.percentage, None)
            if tile_progress.milestone.tile_type == '2':
                self.assertEqual(tile_progress.percentage, 0)
            if tile_progress.milestone.tile_type == '3':
                self.assertEqual(tile_progress.percentage, 0)
            if tile_progress.milestone.tile_type == '4':
                self.assertEqual(tile_progress.percentage, 75)
            if tile_progress.milestone.tile_type == '5':
                self.assertEqual(tile_progress.percentage, 0)
            if tile_progress.milestone.tile_type == '6':
                self.assertEqual(tile_progress.percentage, None)
            if tile_progress.milestone.tile_type == '7':
                self.assertEqual(tile_progress.percentage, 0)


@ddt.ddt
class GetCourseObject(TestCase):
    @ddt.data(
        (1, 'CS101/ORG101/2018'),
        (1, 'test'),
    )
    @ddt.unpack
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    @httpretty.activate
    def test_get_course_object(self, user_id, course_id):
        test_course_data.setup_course_response(course_id="CS101/ORG101/2018", username="")
        test_user_data.setup_user_courses_response(user_id=1)

        course = get_course_object(user_id, course_id)
        if course:
            self.assertEqual(course.id, course_id)
        else:
            self.assertEqual(course, None)


class CreateProgressObjects(TestCase):
    def setUp(self):
        self.user = TestUser(user_id=1, email='mcka_admin_user@mckinseyacademy.com', username='mcka_admin_user')
        self.client = Client()

        self.learner_dashboard = LearnerDashboard(
            title='sample',
            description='sample tile',
            title_color='red',
            description_color='black',
            client_id=1,
            course_id='CS101/ORG101/2018'
        )
        self.learner_dashboard.save()

        self.learner_dashboard_tile_form = {
            'track_progress': '',
            'label': 'sample label',
            'title': 'sample title',
            'note': 'sample note',
            'link': '/learnerdashboard/courses/CS101/ORG101/2018/'
                     'lessons/i4x://zeeqa/qa003/chapter/7a97fd7dc5844534a739abd3f76fe77d/'
                     'module/i4x://zeeqa/qa003/vertical/cfdaa01f1920401fb3805d569fb8a6db/lesson/',  # Lesson,
            'learner_dashboard': self.learner_dashboard.id,
            'label_color': 'red',
            'title_color': 'blue',
            'note_color': 'green',
            'tile_background_color': 'black',
            'tile_type': '2',
            'download_link': 'https://samplelink.com',
            'publish_date': '',
            'background_image': '',
            'start_date': '',
            'end_date': '',
            'show_in_calendar': True,
            'show_in_dashboard': True,
            'hidden_from_learners': False,
            'fa_icon': '',
            'row': '1',
        }

        form = LearnerDashboardTileForm(data=self.learner_dashboard_tile_form)
        form.save()

    def test_createProgressObjects(self):
        request = self.client.get(path='/')
        request.user = self.user

        trackedData = LearnerDashboardTile.objects.filter(
            learner_dashboard=self.learner_dashboard.id,
            show_in_calendar=True
        ).exclude(tile_type='1').exclude(tile_type='6')

        tile_ids = [str(i.id) for i in trackedData]

        progressData = LearnerDashboardTileProgress.objects.filter(milestone_id__in=tile_ids)
        createProgressObjects(progressData, tile_ids, request.user.id)

        learnerdashboard_tileprogress = LearnerDashboardTileProgress.objects.all()
        self.assertEqual(str(learnerdashboard_tileprogress[0].milestone_id), tile_ids[0])
        self.assertEqual(int(learnerdashboard_tileprogress[0].user), request.user.id)
        self.assertEqual(learnerdashboard_tileprogress[0].percentage, 0)


class SocialTotal(TestCase):
    def test_social_total(self):
        user_socials = {str(u_id): social_total(DottableDict(user_metrics)) for u_id, user_metrics in
                        test_course_metrics_data.course_social_metrics["users"].items()
                        }
        for user in list(test_course_metrics_data.course_social_metrics["users"].keys()):
            self.assertEqual(user_socials[user], 10)


class ChooseRandomTaTest(TestCase):
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    @httpretty.activate
    def test_choose_random_ta(self):
        course_id = 'CS101/ORG101/2018'
        test_course_data.setup_get_users_filtered_by_role_response(course_id)

        ta_users_base = ['8', '9']
        additional_fields = ["title", "profile_image", "city", "full_name"]
        test_user_data.setup_get_users_response(ids=ta_users_base, fields=additional_fields)
        ta_users = [user['id'] for user in test_user_data.get_users]

        ta_user = choose_random_ta(course_id)
        self.assertIn(ta_user.id, ta_users)


class GetNonStaffUserTest(TestCase):
    @httpretty.activate
    def test_get_non_staff_user(self):
        course_id = 'CS101/ORG101/2018'
        qs_params = {'fields': 'id,username,is_staff'}
        test_course_data.setup_get_course_details_users_response(course_id, qs_params=qs_params)
        test_course_data.setup_get_users_filtered_by_role_response(course_id)

        non_staff_user = get_non_staff_user(course_id)
        self.assertEqual(non_staff_user['id'], 1)
        self.assertEqual(non_staff_user['username'], 'Jane Doe')
        self.assertEqual(non_staff_user['is_active'], True)


class RemoveDuplicateGrader(TestCase):
    def test_remove_duplicate_grader(self):
        grader_weights = [1, 3, 3]
        graders = []

        for grader_weight in grader_weights:
            grader = mock.Mock()
            grader.weight = grader_weight
            grader.type = settings.GROUP_PROJECT_IDENTIFIER
            graders.append(grader)

        _remove_duplicate_grader(graders)

        self.assertEqual(len(graders), 2)
        for grader in graders:
            self.assertIn(grader.weight, grader_weights)
            self.assertEqual(grader.type, settings.GROUP_PROJECT_IDENTIFIER)


class ResourcePageScriptsFixTest(TestCase):
    def setUp(self):
        self.resource_page_html_with_v3 = '''
        <p></p>
        <h4>Lesson 2: The three-part approach</h4>
        <p></p>
        <p>Senior leaders discuss their approaches to challenging conversations.
        <script src="//player.ooyala.com/v3/635104fd644c4170ae227af2de27deab"></script>
        </p>
        <div id="ooyalaplayer4" style="width: 320px; height: 180px;"></div>
        <p>
        <script>// <![CDATA[
        OO.ready(function() { OO.Player.create('ooyalaplayer4', 'g3bnh0dDq9XsY8MZ-dK_lfcokwM8oXcZ'); });
        // ]]></script>
        <noscript><div>Please enable Javascript to watch this video</div></noscript></p>
        '''

        self.resource_page_without_v3 = '''
        <p></p>
        <table style="border: none;">
        <tbody>
        <tr>
        <td width="120"><img src="/static/endoflessonicons_resources.png" /></td>
        <td width="600">
        <div id="iguide" class="label-5">Jump to section:</div>
        <h2><a href="#iguide"><i class="fa fa-fw"></i><i class="fa fa-level-down"></i> Informational guides</a></h2>
        <h2><a href="#takeaways"><i class="fa fa-fw"></i><i class="fa fa-level-down"></i> Key takeaways, frameworks,
         and additional practice</a></h2>
        <h2><a href="#scontent"><i class="fa fa-fw"></i><i class="fa fa-level-down"></i> Supplementary content</a></h2>
        </td>
        </tr>
        </tbody>
        </table>
        <p></p>
        '''

    def test_v3_scripts_removal(self):
        """
        Tests that v3 scripts are removed from page html
        """
        processed_html = fix_resource_page_video_scripts(self.resource_page_html_with_v3)

        resource_page_soup = BeautifulSoup(processed_html, "html.parser")

        for script_tag in resource_page_soup.find_all('script'):
            self.assertNotIn('player.ooyala.com/v3/', script_tag.attrs.get('src', ''))

    def test_v4_script_inclusion(self):
        """
        Tests that v4 script is being added in page
        """
        processed_html = fix_resource_page_video_scripts(self.resource_page_html_with_v3)

        resource_page_soup = BeautifulSoup(processed_html, "html.parser")

        first_element_src = resource_page_soup.contents[0].attrs.get('src', '')

        self.assertEqual(first_element_src, settings.OOYALA_PLAYER_V4_SCRIPT_FILE)


@ddt.ddt
class GetLearnerDashboard(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.user = TestUser(user_id=1, email='mcka_admin_user@mckinseyacademy.com', username='mcka_admin_user')
        self.client = Client()
        self.course = MockCourseAPI._get_course('CS101/ORG101/2018', force_course_id='CS101/ORG101/2018')

        self.get_basic_user_data = self.apply_patch('courses.controller.get_basic_user_data')
        self.get_basic_user_data.return_value = DottableDict({
            'organization': mock.Mock(display_name='Test program')
        })

        self.learner_dashboard = LearnerDashboard(
            title='sample',
            description='sample tile',
            title_color='red',
            description_color='black',
            client_id=1,
            course_id='CS101/ORG101/2018'
        )
        self.learner_dashboard.save()

        self.learner_dashboard_tile_form = {
            'track_progress': '',
            'label': 'sample label',
            'title': 'sample title',
            'note': 'sample note',
            'link': '/learnerdashboard/courses/CS101/ORG101/2018/'
                     'lessons/i4x://zeeqa/qa003/chapter/7a97fd7dc5844534a739abd3f76fe77d/'
                     'module/i4x://zeeqa/qa003/vertical/cfdaa01f1920401fb3805d569fb8a6db/lesson/',  # Lesson,
            'learner_dashboard': self.learner_dashboard.id,
            'label_color': 'red',
            'title_color': 'blue',
            'note_color': 'green',
            'tile_background_color': 'black',
            'tile_type': '2',
            'download_link': 'https://samplelink.com',
            'publish_date': '',
            'background_image': '',
            'start_date': '',
            'end_date': '',
            'show_in_calendar': True,
            'show_in_dashboard': True,
            'hidden_from_learners': False,
            'fa_icon': '',
            'row': '1',
        }
        form = LearnerDashboardTileForm(data=self.learner_dashboard_tile_form)
        form.save()

        self.feature_flags = FeatureFlags(
            course_id=self.course.id,
            learner_dashboard=True
        )
        self.feature_flags.save()

    @ddt.data(
        True, False
    )
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_get_learner_dashboard(self, learner_dashboard_enabled):
        request = self.client.get(path='/')
        request.user = self.user
        request.session = {'session_key': ''}

        settings = self.apply_patch('courses.controller.settings')
        settings.LEARNER_DASHBOARD_ENABLED = learner_dashboard_enabled

        learner_dashboard = get_learner_dashboard(request, self.course.id)
        if learner_dashboard_enabled:
            self.assertEqual(learner_dashboard.title, 'sample')
            self.assertEqual(learner_dashboard.description, 'sample tile')
            self.assertEqual(learner_dashboard.title_color, 'red')
            self.assertEqual(learner_dashboard.description_color, 'black')
            self.assertEqual(learner_dashboard.client_id, 1)
            self.assertEqual(learner_dashboard.course_id, self.course.id)
        else:
            self.assertEqual(learner_dashboard, None)

    @ddt.data(
        True, False
    )
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_get_user_learner_dashboards(self, learner_dashboard_enabled):
        request = self.client.get(path='/')
        settings = self.apply_patch('courses.controller.settings')
        settings.LEARNER_DASHBOARD_ENABLED = learner_dashboard_enabled

        learner_dashboards = user_learner_dashboards(request, [self.course])
        if learner_dashboard_enabled:
            for learner_dashboard in learner_dashboards:
                self.assertTrue(learner_dashboard.calendar_enabled, True)
                self.assertTrue(learner_dashboard.features.learner_dashboard, True)
        else:
            self.assertEqual(learner_dashboards, [])
