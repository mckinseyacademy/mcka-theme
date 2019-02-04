import httpretty

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
