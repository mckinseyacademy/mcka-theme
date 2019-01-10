import json
from urlparse import urlparse, parse_qs

import ddt
import httpretty
from django.conf import settings
from django.test import TestCase, override_settings
from mock import patch

from accounts.helpers import TestUser
from api_client.course_api import (
    COURSEWARE_API,
    COURSE_COHORTS_API,
    COURSE_COMPLETION_API,
    get_course,
    get_course_cohort_settings,
    get_course_completions,
    get_course_enrollments,
    get_course_list_for_manager_reports,
    get_manager_reports_in_course,
)
from api_client.json_object import JsonParser
from mcka_apros.settings import COURSE_ENROLLMENT_API


@ddt.ddt
class TestCourseApi(TestCase):
    """
    Test the Course API calls
    """
    COURSE_ID = 'test/course/1'
    DEPTH = 10
    TEST_USER = TestUser(11, 'user1@example.com', 'test_user_1')
    STAFF_USER = TestUser(12, 'staff@example.com', 'staff_user_1', is_staff=True)
    USER_DICT = dict(id=11, email='user1@example.com', username='test_user_1')

    def setUp(self):
        """
        Create stub for the courseware API.
        """
        super(TestCourseApi, self).setUp()

        # normal users get empty course response
        self.empty_course_response = '''{
            "category":"course",
            "end":null,
            "name":"Test course",
            "uri":"http://lms.mcka.local:8000/api/server/courses/test/course/1",
            "due":null,
            "number":"course",
            "content":[],
            "start":"2016-01-01T00:00:00Z",
            "org":"OpenCraft",
            "id":"test/course/1",
            "resources":[],
            "course_image_url":"/c4x/test/course/asset/logo.png"
        }'''

        # Staff user gets a course with a chapter
        self.course_response = '''{
          "category":"course",
          "end":null,
          "name":"Test course",
          "uri":"http://lms.mcka.local:8000/api/server/courses/test/course/1",
          "due":null,
          "number":"course",
          "content":[
            {
              "category": "chapter",
                "children": [
                  {
                    "category": "sequential",
                    "children": [
                      {
                        "category": "pb-instructor-tool",
                        "children": [],
                        "due": null,
                        "end": null,
                        "id": "i4x://OpenCraft/MCKIN-5434/pb-instructor-tool/07ba964de0c4485d8163b8ba8eb84324",
                        "name": "Instructor Tool",
                        "start": "2016-01-01T00:00:00Z",
                        "uri": "http://lms.mcka.local:8000/...-instructor-tool/07ba964de0c4485d8163b8ba8eb84324"
                      }
                    ],
                    "due": null,
                    "end": null,
                    "id": "i4x://test/course/sequential/432e55fd201d46aea2ddf815e54e83cb",
                    "name": "Instructor Tool",
                    "start": "2016-01-01T00:00:00Z",
                    "uri": "http://lms.mcka.local:8000/...sequential/432e55fd201d46aea2ddf815e54e83cb"
                  }
                ],
                "due": null,
                "end": null,
                "id": "i4x://test/course/chapter/17419866267c4ce29ec0558ef21cbfe1",
                "name": "Features",
                "start": "2016-01-01T00:00:00Z",
                "uri": "http://lms.mcka.local:8000/...chapter/17419866267c4ce29ec0558ef21cbfe1"
            }
          ],
          "start":"2016-01-01T00:00:00Z",
          "org":"OpenCraft",
          "id":"test/course/1",
          "resources":[],
          "course_image_url":"/c4x/test/course/asset/logo.png"
        }'''

        self.enrollment_api_response = """
        {
          "count": 6,
          "num_pages": 1,
          "current_page": 1,
          "results": [
            {
              "created": "2018-04-22T05:58:04.008954Z",
              "mode": "verified",
              "is_active": true,
              "user": "edx",
              "course_id": "course-v1:edX+DemoX+Demo_Course"
            },
            {
              "created": "2018-06-27T06:19:34.282080Z",
              "mode": "audit",
              "is_active": true,
              "user": "edx",
              "course_id": "course-v1:OpenCraft+EOCJ001+2018_1"
            },
            {
              "created": "2017-06-07T00:44:28.308850Z",
              "mode": "audit",
              "is_active": true,
              "user": "honor",
              "course_id": "course-v1:edX+DemoX+Demo_Course"
            },
            {
              "created": "2017-06-07T00:44:32.887985Z",
              "mode": "audit",
              "is_active": true,
              "user": "audit",
              "course_id": "course-v1:edX+DemoX+Demo_Course"
            },
            {
              "created": "2017-06-07T00:44:37.447686Z",
              "mode": "audit",
              "is_active": true,
              "user": "verified",
              "course_id": "course-v1:edX+DemoX+Demo_Course"
            },
            {
              "created": "2017-06-07T00:44:41.997373Z",
              "mode": "audit",
              "is_active": true,
              "user": "staff",
              "course_id": "course-v1:edX+DemoX+Demo_Course"
            }
          ],
          "next": null,
          "start": 0,
          "previous": null
        }
        """

    def _setup_courseware_response(self):
        """
        Stub out the courseware API
        """

        def courseware_response(request, uri, headers):  # pylint: disable=unused-argument
            # staff user gets the course with 1 chapter
            if self.STAFF_USER.username in uri:
                return (200, headers, self.course_response)

            # if no user is passed, then a generic course response is returned
            # Everyone else gets the "empty course"
            return (200, headers, self.empty_course_response)

        httpretty.register_uri(
            httpretty.GET,
            '{}/{}/{}'.format(
                settings.API_SERVER_ADDRESS,
                COURSEWARE_API,
                self.COURSE_ID,
            ),
            body=courseware_response,
            status=200,
            content_type='application/json',
        )

    @ddt.data(
        # Test with positional arguments
        ([COURSE_ID], {}, 0),
        ([COURSE_ID, DEPTH], {}, 0),
        ([COURSE_ID, DEPTH, TEST_USER], {}, 0),
        ([COURSE_ID, DEPTH], dict(user=TEST_USER), 0),
        # Test with keyword arguments
        ([COURSE_ID], dict(depth=DEPTH), 0),
        ([COURSE_ID], dict(depth=DEPTH, user=TEST_USER), 0),
        # Test with dict user
        ([COURSE_ID], dict(depth=DEPTH, user=USER_DICT), 0),
    )
    @ddt.unpack
    @httpretty.activate
    def test_get_course(self, args, kwargs, expected_result):
        """
        Test get_course with positional and keyword argments.
        """
        self._setup_courseware_response()
        course = get_course(*args, **kwargs)
        self.assertEquals(len(course.chapters), expected_result)

    @httpretty.activate
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_get_course_different_users(self):
        """
        Ensure that get_course can return different content for different users.
        """
        self._setup_courseware_response()
        course2 = get_course(course_id=self.COURSE_ID, depth=self.DEPTH, user=self.TEST_USER)
        course1 = get_course(course_id=self.COURSE_ID, depth=self.DEPTH, user=self.STAFF_USER)

        self.assertNotEqual(course1, course2)
        self.assertEquals(len(course1.chapters), 1)
        self.assertEquals(len(course2.chapters), 0)

    def _setup_enrollment_response(self):
        def _filter_by_usernames(data, usernames):
            if usernames is None:
                return data
            usernames = usernames[0].split(',')
            return [
                item for item in data
                if item['user'] in usernames
            ]

        def _filter_by_course(data, course_id):
            if course_id is None:
                return data
            return [
                item for item in data
                if item['course_id'] == course_id[0]
            ]

        def enrollment_api_response(request, uri, headers):  # pylint: disable=unused-argument
            query_params = parse_qs(urlparse(uri).query)
            data = json.loads(self.enrollment_api_response)['results']
            data = _filter_by_usernames(data, query_params.get('username'))
            data = _filter_by_course(data, query_params.get('course_id'))
            response = json.dumps({
                'pagination': {
                    'next': None,
                    'count': len(data)
                },
                'results': data
            })
            return 200, headers, response
        httpretty.register_uri(
            httpretty.GET,
            '{}/{}'.format(
                settings.API_SERVER_ADDRESS,
                COURSE_ENROLLMENT_API,
                match_querystring=False,
            ),
            body=enrollment_api_response,
            status=200,
            content_type='application/json',
        )

    @ddt.data(
        # No filter
        {'course_id': None, 'usernames': None, 'count': 6},
        # No users
        {'course_id': 'course-v1:edX+DemoX+Demo_Course', 'usernames': [], 'count': 0},
        {'course_id': 'course-v1:edX+DemoX+Demo_Course', 'usernames': None, 'count': 5},
        {'course_id': 'course-v1:edX+DemoX+Demo_Course', 'usernames': ['edx'], 'count': 1},
        {'course_id': None, 'usernames': ['edx'], 'count': 2},
        {'course_id': None, 'usernames': ['edx', 'honor'], 'count': 3},
        {'course_id': 'course-v1:edX+DemoX+Demo_Course', 'usernames': ['edx', 'honor'], 'count': 2},
    )
    @ddt.unpack
    @httpretty.httprettified
    def test_get_course_enrollments(self, course_id, usernames, count):
        self._setup_enrollment_response()
        data = get_course_enrollments(course_id, usernames)
        self.assertEqual(len(data), count)

    @httpretty.httprettified
    @patch('api_client.course_api.get_reports_for_manager')
    def test_get_course_list_for_manager_reports(self, mock_get_reports_for_manager):
        self._setup_enrollment_response()
        mock_get_reports_for_manager.return_value = JsonParser.from_dictionary([
            {'username': 'edx'},
            {'username': 'honor'},
        ])
        data = get_course_list_for_manager_reports('staff@example.com')
        self.assertEqual(data, [u'course-v1:OpenCraft+EOCJ001+2018_1', u'course-v1:edX+DemoX+Demo_Course'])

    @httpretty.httprettified
    @patch('api_client.course_api.get_reports_for_manager')
    def test_get_manager_reports_in_course(self, mock_get_reports_for_manager):
        self._setup_enrollment_response()
        mock_get_reports_for_manager.return_value = JsonParser.from_dictionary([
            {'username': 'edx'},
            {'username': 'honor'},
            {'username': 'noone'},
        ])
        data = get_manager_reports_in_course('staff@example.com', 'course-v1:edX+DemoX+Demo_Course')
        self.assertEqual(data, [u'edx', u'honor'])

    @ddt.data(
        ('{"is_cohorted": true, "id": 1}', True),
        ('{"is_cohorted": false, "id": 1}', False),
    )
    @ddt.unpack
    @httpretty.httprettified
    def test_get_course_cohort_settings(self, body, is_cohorted):
        def cohort_settings_response(request, uri, headers):
            return (200, headers, body)

        httpretty.register_uri(
            httpretty.GET,
            '{}/{}/settings/{}'.format(
                settings.API_SERVER_ADDRESS,
                COURSE_COHORTS_API,
                self.COURSE_ID,
            ),
            body=cohort_settings_response,
            status=200,
            content_type='application/json'
        )
        cohort_settings = get_course_cohort_settings(self.COURSE_ID)
        self.assertEqual(cohort_settings.is_cohorted, is_cohorted)

    @ddt.data(
        {
            'extra_fields': 'all',
            'response': {'requested_fields': ['chapter', 'sequential', 'vertical']}
        },
        {
            'extra_fields': 'chapter,vertical',
            'response': {'requested_fields': ['chapter', 'vertical']}
        },
        {
            'username': 'edx',
            'response': {'username': 'edx'}
        },
        {
            'root_block': 'root_block',
            'response': {'root_block': 'root_block'}
        },
    )
    @ddt.unpack
    @patch('api_client.course_api.group_completions_by_course')
    @patch('api_client.course_api.group_completions_by_user')
    @httpretty.httprettified
    def test_get_course_completions_filtering_ids(
        self,
        mock_group_completions_by_course,
        mock_group_completions_by_user,
        extra_fields=None,
        username=None,
        user_ids=None,
        root_block=None,
        response=None,
    ):
        """
        Test if the course completions arguments are correctly passed by
        """
        course_id = 'course-v1:edX+DemoX+Demo_Course'

        # Mock parsing of request response
        mock_group_completions_by_course.return_value = 'course'
        mock_group_completions_by_user.return_value = 'user'

        def course_completions_response(request, _uri, headers, correct_response=response):
            self.assertEqual(correct_response, json.loads(request.body))
            return (200, headers, json.dumps({
                'results': []
            }))

        httpretty.register_uri(
            httpretty.POST,
            '{api_base}/{course_completion_api}/{course_id}/?page_size=200'.format(
                api_base=settings.API_SERVER_ADDRESS,
                course_completion_api=COURSE_COMPLETION_API,
                course_id=course_id,
            ),
            body=course_completions_response,
            status=200,
            content_type='application/json'
        )

        course_completions = get_course_completions(
            course_id=course_id,
            extra_fields=extra_fields,
            username=username,
            user_ids=user_ids,
            root_block=root_block,
        )

        # Check if correct parsing function was called
        if user_ids:
            self.assertEqual(course_completions, 'user')
        else:
            self.assertEqual(course_completions, 'course')

    @patch('api_client.course_api.group_completions_by_course')
    @httpretty.httprettified
    def test_get_course_completions_by_user(
        self,
        mock_group_completions_by_course,
    ):
        """
        Test if the course completions arguments are correct
        """

        mock_group_completions_by_course.return_value = 'by_course'

        def course_completions_response(_request, _uri, headers):
            return (200, headers, json.dumps({
                'results': []
            }))

        httpretty.register_uri(
            httpretty.GET,
            '{api_base}/{course_completion_api}/?{username}&page_size=200'.format(
                api_base=settings.API_SERVER_ADDRESS,
                course_completion_api=COURSE_COMPLETION_API,
                username='edx',
            ),
            body=course_completions_response,
            status=200,
            content_type='application/json'
        )

        result = get_course_completions(
            username='edx',
            extra_fields=None
        )
        self.assertEqual(result, 'by_course')
