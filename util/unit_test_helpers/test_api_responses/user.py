import json
import httpretty
from urllib import urlencode

from django.conf import settings

from api_client.user_api import USER_API


def setup_user_profile_response(user_id, response=None):
    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        USER_API,
        user_id
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=response or user_profile,
        status=200,
        content_type='application/json',
    )


def setup_user_courses_response(user_id, response=None):
    url = '{}/{}/{}/courses'.format(
        settings.API_SERVER_ADDRESS,
        USER_API,
        user_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=response or user_courses,
        status=200,
        content_type='application/json',
    )


def setup_get_users_response(fields=[], *args, **kwargs):
    request_fields = ['id', 'email', 'first_name', 'username', 'is_active']
    request_fields.extend(fields)

    qs_params = {
        'page_size': 0,
        'fields': ','.join(request_fields),
        'ids': ','.join(kwargs['ids']),
    }
    url = '{}/{}?{}'.format(
        settings.API_SERVER_ADDRESS,
        USER_API,
        urlencode(qs_params)
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(get_users),
        status=200,
        content_type='application/json',
    )


def setup_get_user_workgroups_response(user_id, course_id=None):
    qs_params = {"page_size": 0}
    if course_id:
        qs_params["course_id"] = course_id

    url = '{}/{}/{}/workgroups/?{}'.format(
        settings.API_SERVER_ADDRESS,
        USER_API,
        user_id,
        urlencode(qs_params),
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(user_workgroups),
        status=200,
        content_type='application/json',
    )


user_profile = '''{
    "username": "mcka_admin_user",
    "city": "",
    "first_name": "Mcka",
    "last_name": "Admin",
    "created": "2018-03-21T14:08:52.745Z",
    "country": "",
    "title": "Mr.",
    "is_active": true,
    "uri": "http://lms.mcka.local/api/server/users/1",
    "profile_image": {
        "image_url_full": "/media/profile-images/886e752c789cb51a21f2b176d656463d_500.jpg?v=1538433362",
        "image_url_large": "/media/profile-images/886e752c789cb51a21f2b176d656463d_120.jpg?v=1538433362",
        "image_url_medium": "/media/profile-images/886e752c789cb51a21f2b176d656463d_50.jpg?v=1538433362",
        "image_url_small": "/media/profile-images/886e752c789cb51a21f2b176d656463d_30.jpg?v=1538433362",
        "has_image": true
    },
    "id": 1,
    "year_of_birth": 2014,
    "is_staff": true,
    "last_login": "2019-01-14T13:56:20.123Z",
    "full_name": "Mcka Admin",
    "gender": "M",
    "email": "mcka_admin_user@mckinseyacademy.com",
    "resources": [
        {
            "uri": "http://lms.mcka.local/api/server/users/1/groups"
        },
        {
            "uri": "http://lms.mcka.local/api/server/users/1/courses"
        }
    ],
    "level_of_education": ""
}'''

user_courses = '''[
    {
        "end": "2021-01-01T00:00:00Z",
        "name": "Marketing & Sales Fundamentals",
        "learner_dashboard": false,
        "is_active": true,
        "uri": "http://lms.mcka.local/api/server/users/1/courses//IssueORG/Issue101/2018_T2",
        "start": "2016-08-31T00:00:00Z",
        "id": "CS101/ORG101/2018",
        "course_image_url": "/c4x/'CS101/ORG101/asset/MS_Course-Overview.png"
    },
    {
        "end": "2017-02-09T23:00:00Z",
        "name": "[Test] Business Strategy Jan 2016",
        "learner_dashboard": false,
        "is_active": true,
        "uri": "http://lms.mcka.local/api/server/users/1/courses//org105/ABC101/2018_T1",
        "start": "2015-10-29T01:00:00Z",
        "id": "org105/ABC101/2018_T1",
        "course_image_url": "/c4x/org105/ABC101/asset/McKA_course_tile_BusStrat.png"
    }
]'''

get_users = [
    {
        "id": 8,
        "email": "mcka_admin_user@mckinseyacademy.com",
        "username": "mcka_admin_user",
        "first_name": "mcka_admin_user",
        "last_name": "Tester",
        "is_active": True,
        "city": "New York",
        "title": "",
        "country": "",
        "full_name": "mcka_admin_user Tester",
        "profile_image": {
            "image_url_full": "/media/profile-images/886e752c789cb51a21f2b176d656463d_500.jpg?v=1538433362",
            "image_url_large": "/media/profile-images/886e752c789cb51a21f2b176d656463d_120.jpg?v=1538433362",
            "image_url_medium": "/media/profile-images/886e752c789cb51a21f2b176d656463d_50.jpg?v=1538433362",
            "image_url_small": "/media/profile-images/886e752c789cb51a21f2b176d656463d_30.jpg?v=1538433362",
            "has_image": True
        }
    },
    {
        "id": 9,
        "email": "mcka_subadmin_user@mckinseyacademy.com",
        "username": "mcka_subadmin_user",
        "first_name": "mcka_subadmin_user",
        "last_name": "Tester",
        "is_active": True,
        "city": "Washington",
        "title": "",
        "country": "",
        "full_name": "mcka_subadmin_user Tester",
        "profile_image": {
            "image_url_full": "/media/profile-images/886e752c789cb51a21f2b176d656463d_500.jpg?v=1538433362",
            "image_url_large": "/media/profile-images/886e752c789cb51a21f2b176d656463d_120.jpg?v=1538433362",
            "image_url_medium": "/media/profile-images/886e752c789cb51a21f2b176d656463d_50.jpg?v=1538433362",
            "image_url_small": "/media/profile-images/886e752c789cb51a21f2b176d656463d_30.jpg?v=1538433362",
            "has_image": True
        }
    },
]

user_workgroups = [
    {
        "created": "2018-11-05T17:44:47.627140Z",
        "date_fields": [],
        "id": 2,
        "modified": "2018-11-05T17:44:48.172694Z",
        "name": "Group 2",
        "object_map": {},
        "project": "http://lms.mcka.local/api/server/projects/1/",
        "required_fields": [],
        "url": "http://lms.mcka.local/api/server/workgroups/2/",
        "valid_fields": None
    }
]
