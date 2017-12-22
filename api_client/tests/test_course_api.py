from django.test import TestCase
from django.conf import settings
import ddt
import httpretty

from accounts.helpers import TestUser
from api_client.course_api import get_course, COURSEWARE_API


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

    def _setup_courseware_response(self):
        """
        Stub out the courseware API
        """

        def courseware_response(request, uri, headers):  # pylint: disable=unused-argument
            # staff user gets the course with 1 chapter
            if self.STAFF_USER.username in uri:
                return (200, headers, self.course_response)

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
        ([COURSE_ID], {}),
        ([COURSE_ID, DEPTH], {}),
        ([COURSE_ID, DEPTH, TEST_USER], {}),
        ([COURSE_ID, DEPTH], dict(user=TEST_USER)),
        # Test with keyword arguments
        ([COURSE_ID], dict(depth=DEPTH)),
        ([COURSE_ID], dict(depth=DEPTH, user=TEST_USER)),
        # Test with dict user
        ([COURSE_ID], dict(depth=DEPTH, user=USER_DICT)),
    )
    @ddt.unpack
    @httpretty.activate
    def test_get_course(self, args, kwargs):
        """
        Test get_course with positional and keyword argments.
        """
        self._setup_courseware_response()
        course = get_course(*args, **kwargs)
        self.assertEquals(len(course.chapters), 0)

    @httpretty.activate
    def test_get_course_different_users(self):
        """
        Ensure that get_course can return different content for different users.
        """
        self._setup_courseware_response()
        course1 = get_course(course_id=self.COURSE_ID, depth=self.DEPTH, user=self.STAFF_USER)
        course2 = get_course(course_id=self.COURSE_ID, depth=self.DEPTH, user=self.TEST_USER)

        self.assertNotEqual(course1, course2)
        self.assertEquals(len(course1.chapters), 1)
        self.assertEquals(len(course2.chapters), 0)
