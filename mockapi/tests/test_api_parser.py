from django.test import TestCase
from django.conf import settings

import json

from mockapi.models import MockHttpResponse
from mockapi.api_parser import ApiParser

# Create your tests here.


class MockerTester(TestCase):

    def test_simple(self):
        response_dictionary = {
            "documentation": "http://docs.openedxapi.apiary.io",
            "name": "Open edX API",
            "uri": "/api",
            "description": "Machine interface for interactions with Open edX.",
            "resources": [
                {
                    "uri": "/api/groups",
                    "uri": "/api/sessions",
                    "uri": "/api/system",
                    "uri": "/api/users",
                }
            ]
        }
        test_data = (
            '### GET /api\n'
            '+ Response 200 (application/json)\n'
            '    + Body\n'
            '            {}'.format(json.dumps(response_dictionary))
        )

        mock_response = MockHttpResponse(test_data)

        self.assertEqual(mock_response._method, "GET")
        self.assertEqual(mock_response._address, "/api")
        self.assertEqual(mock_response._code, 200)
        self.assertEqual(mock_response._content_type, "application/json")

        responded_dictionary = json.loads(mock_response._response_body)
        self.assertEqual(responded_dictionary, response_dictionary)

    def test_parameters(self):
        '''
        Parameters is set for documentation - we ignore
        '''
        response_dictionary = [
            {
                "category": "html",
                "uri": "http://openedxapi.apiary-mock.com/api/courses/edX/Open_DemoX/edx_demo_course/modules/i4x://edX/Open_DemoX/html/030e35c4756a4ddc8d40b95fbbfff4d4",
                "id": "i4x://edX/Open_DemoX/html/030e35c4756a4ddc8d40b95fbbfff4d4",
                "name": "Blank HTML Page"
            },
            {
                "category": "video",
                "uri": "http://openedxapi.apiary-mock.com/api/courses/edX/Open_DemoX/edx_demo_course/modules/i4x://edX/Open_DemoX/video/0b9e39477cf34507a7a48f74be381fdd",
                "id": "i4x://edX/Open_DemoX/video/0b9e39477cf34507a7a48f74be381fdd",
                "name": "Welcome!"
            }
        ]

        body_string = '            {}'.format(json.dumps(response_dictionary))
        test_data = (
            '### GET /api/courses/{course_id}/modules/{module_id}/submodules{?type}\n'
            '+ Parameters\n'
            '    + type (optional, string) ... module category filter\n'
            '+ Response 200\n'
            '    + Body\n'
        )
        test_data += body_string

        mock_response = MockHttpResponse(test_data)

        self.assertEqual(mock_response._method, "GET")
        self.assertEqual(
            mock_response._address, "/api/courses/{course_id}/modules/{module_id}/submodules{?type}")
        self.assertEqual(mock_response._code, 200)
        self.assertTrue(mock_response._content_type is None)

        responded_dictionary = json.loads(mock_response._response_body)
        self.assertEqual(responded_dictionary, response_dictionary)

    def test_post(self):
# POST /api/groups
# + Request (application/json)

#     + Body

#             {
#                 "name": "Alpha Group"
#             }

# + Response 201 (application/json)

#     + Body

#             {
#                 "name": "Alpha Group",
#                 "id": 98734,
#                 "uri": "http://openedxapi.apiary-mock.com/api/groups/2468"
#             }

        request_dictionary = {
            "name": "Alpha Group"
        }

        response_dictionary = {
            "name": "Alpha Group",
            "id": 98734,
            "uri": "http://openedxapi.apiary-mock.com/api/groups/2468"
        }

        test_data = (
            '### POST /api/groups\n'
            '+ Request (application/json)\n'
            '    + Body\n'
            '            {}\n'
            '+ Response 201 (application/json)\n'
            '    + Body\n'
            '            {}\n'
        )

        test_data = test_data.format(
            json.dumps(request_dictionary), json.dumps(response_dictionary))
        mock_response = MockHttpResponse(test_data)

        self.assertEqual(mock_response._method, "POST")
        self.assertEqual(mock_response._address, "/api/groups")
        self.assertEqual(mock_response._code, 201)
        self.assertEqual(mock_response._content_type, "application/json")

        responded_dictionary = json.loads(mock_response._response_body)
        self.assertEqual(responded_dictionary, response_dictionary)

        # Now check that POST request checks only format, not content of
        # request data
        test_request_body = json.dumps({
            "name": "Fake Group Name"
        })
        self.assertTrue(mock_response.check_post_format(test_request_body))

    
    def test_delete(self):
        test_data = (
            '### DELETE /api/groups/{group_id}\n'
            '+ Response 204\n'
        )

        mock_response = MockHttpResponse(test_data)

        self.assertEqual(mock_response._method, "DELETE")
        self.assertEqual(mock_response._address, "/api/groups/{group_id}")
        self.assertEqual(mock_response._code, 204)
        self.assertEqual(mock_response._content_type, None)

    def test_api_parser(self):
        mock_responses = ApiParser(settings.LOCAL_MOCK_API_FILES).responses()

        #self.assertEqual(len(mock_responses), 30)
        self.assertEqual(mock_responses[0]._method, "GET")

        response_dictionary = json.loads(mock_responses[0]._response_body)
        expected_dictionary = {
            "documentation": "http://docs.openedxapi.apiary.io", 
            "name": "Open edX API", 
            "uri": "http://openedxapi.apiary-mock.com/api/", 
            "description": "Machine interface for interactions with Open edX.",
            "resources": [
                {
                    "uri": "http://openedxapi.apiary-mock.com/api/courses"
                }, 
                {
                    "uri": "http://openedxapi.apiary-mock.com/api/groups"
                }, 
                {
                    "uri": "http://openedxapi.apiary-mock.com/api/sessions"
                }, 
                {
                    "uri": "http://openedxapi.apiary-mock.com/api/system"
                }, 
                {
                    "uri": "http://openedxapi.apiary-mock.com/api/users"
                }
            ]
        }

        self.assertEqual(response_dictionary, expected_dictionary)

        # now make sure that all responses are well-formatted json
        for mock_response in mock_responses:
            if mock_response._code != 204:
                try:
                    json.loads(mock_response._response_body)
                except:
                    print 'Badly formed json for mock response {} {}'.format(mock_response._method, mock_response._address)
                    raise

    def test_rebuild_url(self):
        url = r"/api/courses/edX/Open_DemoX/edx_demo_course/modules/i4x://edX/Open_DemoX/chapter/d8a6192ade314473a78242dfeedfbf5b"
        url_chunks = url.split('/')
        new_url = '/'.join(url_chunks)

        self.assertEqual(new_url, url)
