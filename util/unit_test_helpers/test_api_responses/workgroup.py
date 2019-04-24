import json
import httpretty

from django.conf import settings

from api_client.workgroup_api import WORKGROUP_API
from api_client.group_api import GROUP_API


def setup_get_workgroup_users_response(workgroup_id):
    url = '{}/{}/{}/users/'.format(
        settings.API_SERVER_ADDRESS,
        WORKGROUP_API,
        workgroup_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(workgroup_users),
        status=200,
        content_type='application/json',
    )


def setup_get_workgroup_response(workgroup_id):
    ''' fetch workgroup by id '''
    url = '{}/{}/{}/'.format(
        settings.API_SERVER_ADDRESS,
        WORKGROUP_API,
        workgroup_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(workgroup),
        status=200,
        content_type='application/json',
    )


def setup_get_workgroup_review_items_response(workgroup_id):
    url = '{}/{}/{}/workgroup_reviews/'.format(
        settings.API_SERVER_ADDRESS,
        WORKGROUP_API,
        workgroup_id
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(workgroup_reviews),
        status=200,
        content_type='application/json',
    )


def setup_get_workgroup_groups_response(workgroup_id):

    url = '{}/{}/{}/groups/'.format(
        settings.API_SERVER_ADDRESS,
        WORKGROUP_API,
        workgroup_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(workgroup_groups),
        status=200,
        content_type='application/json',
    )


def setup_get_users_in_group_response(group_id):
    url = '{}/{}/{}/users'.format(
        settings.API_SERVER_ADDRESS,
        GROUP_API,
        group_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(workgroup),
        status=200,
        content_type='application/json',
    )


workgroup_groups = [
    {
        "id": 2,
        "url": "http://lms.mcka.local/api/server/groups/2/",
        "name": "mcka obeserver",
        "type": "permission",
        "data": {
            "xblock_id": "i4x://Organization_Y/CS105/gp-v2-activity/2a4e4bb9b329420b84007d7e13f8a876"
        }
    },
    {
        "id": 10,
        "url": "http://lms.mcka.local/api/server/groups/10/",
        "name": "mcka_role_mcka_subadmin",
        "type": "permission",
        "data": {
            "xblock_id": "i4x://Organization_Y/CS105/gp-v2-activity/b5da0da34d444428a15cf4a70b42bz31"
        }
    }
]

workgroup_users = [
    {
        "date_fields": [],
        "email": "mcka_ta_user@mckinseyacademy.com",
        "id": 8,
        "object_map": {},
        "required_fields": [],
        "url": "http://lms.mcka.local/user_api/v1/users/9/",
        "username": "mcka_ta_useruser_list",
        "valid_fields": None
    },
    {
        "date_fields": [],
        "email": "orguser100@mailinator.com",
        "id": 9,
        "object_map": {},
        "required_fields": [],
        "url": "http://lms.mcka.local/user_api/v1/users/114/",
        "username": "orguser100",
        "valid_fields": None
    }
]

workgroup = {
    "id": 2,
    "url": "http://lms.mcka.local/api/server/workgroups/2/",
    "created": "2014-06-26T09:46:09Z",
    "modified": "2014-08-08T09:45:24Z",
    "name": "Group 2",
    "project": 1,
    "groups": workgroup_groups,
    "users": workgroup_users,
    "submissions": [],
    "workgroup_reviews": [],
    "peer_reviews": []
}

workgroup_reviews = [
    {
        "id": 89,
        "url": "http://qa.mckinsey.edx.org/api/server/workgroup_reviews/89/",
        "created": "2014-08-05T10:47:31Z",
        "modified": "2014-08-05T10:47:31Z",
        "question": "other_team_q3",
        "answer": "80",
        "workgroup": 2,
        "reviewer": "fdd0f3a1d513b95ecc58255e32afcb64",
        "content_id": "i4x://Organization_Y/CS105/gp-v2-activity/2a4e4bb9b329420b84007d7e13f8a876"
    },
    {
        "id": 90,
        "url": "http://qa.mckinsey.edx.org/api/server/workgroup_reviews/90/",
        "created": "2014-08-05T10:47:31Z",
        "modified": "2014-08-05T10:47:31Z",
        "question": "other_team_q2",
        "answer": "80",
        "workgroup": 2,
        "reviewer": "fdd0f3a1d513b95ecc58255e32afcb64",
        "content_id": "i4x://Organization_Y/CS105/gp-v2-activity/b5da0da34d444428a15cf4a70b42bea3"
    }
]
