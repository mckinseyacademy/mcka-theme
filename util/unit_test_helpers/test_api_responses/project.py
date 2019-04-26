import json
import httpretty

from django.conf import settings

PROJECT_API = getattr(settings, 'PROJECT_API', 'api/server/projects')


def setup_fetch_project_from_url_response(url):
    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(project),
        status=200,
        content_type='application/json',
    )


def setup_get_project_reponse(project_id):
    url = '{}/{}/{}/'.format(
        settings.API_SERVER_ADDRESS,
        PROJECT_API,
        project_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(project),
        status=200,
        content_type='application/json',
    )


project = {
     "content_id": "i4x://Organization_Y/CS105/gp-v2-project/1b4fc43f58a14705bb6c4f0e68f4cbaa",
     "course_id": "Organization_Y/CS105/2018_T5",
     "created": "2018-11-05T16:25:26.595258Z",
     "date_fields": [],
     "id": 1,
     "modified": "2018-11-05T16:25:26.595560Z",
     "object_map": {},
     "organization": None,
     "required_fields": [],
     "url": "http://lms.mcka.local/api/server/projects/1/",
     "valid_fields": None,
     "workgroups": [1, 2]
}

course_group_projects = [
    {
       "activities": [
            {
                "category": "gp-v2-activity",
                "children": [],
                "date_fields": [],
                "due": None,
                "id": "i4x://Organization_Y/CS105/gp-v2-activity/2a4e4bb9b329420b84007d7e13f8a876",
                "link": "/courses/Organization_Y/CS105/2018_T5/group_work?activate_block_id="
                        "i4x%3A%2F%2FOrganization_Y%2FCS105%2Fgp-v2-activity%2F2a4e4bb9b329420b84007d7e13f8a876",
                "name": 'Kickoff',
                "object_map": {},
                "required_fields": [],
                "start": "2015-10-29T01:00:00Z",
                "uri": "http://lms.mcka.local/api/server/courses/Organization_Y/CS105/2018_T5/content/"
                       "i4x://Organization_Y/CS105/gp-v2-activity/2a4e4bb9b329420b84007d7e13f8a876",
                "valid_fields": None,
            },
            {
                "category": "gp-v2-activity",
                "children": [],
                "date_fields": [],
                "due": None,
                "id": "i4x://Organization_Y/CS105/gp-v2-activity/b5da0da34d444428a15cf4a70b42bea3",
                "link": "/courses/Organization_Y/CS105/2018_T5/group_work?activate_block_id="
                        "i4x%3A%2F%2FOrganization_Y%2FCS105%2Fgp-v2-activity%2Fb5da0da34d444428a15cf4a70b42bea3",
                "name": "Strategy Table",
                "object_map": {},
                "required_fields": [],
                "start": "2015-10-29T01:00:00Z",
                "uri": "http://lms.mcka.local/api/server/courses/Organization_Y/CS105/2018_T5/content/"
                       "i4x://Organization_Y/CS105/gp-v2-activity/b5da0da34d444428a15cf4a70b42bea3",
                "valid_fields": None,
            },
            {
                "category": "gp-v2-activity",
                "children": [],
                "date_fields": [],
                "due": None,
                "id": "i4x://Organization_Y/CS105/gp-v2-activity/382a80f3f706441799e620417e60f5b6",
                "link": "/courses/Organization_Y/CS105/2018_T5/group_work?activate_block_id="
                        "i4x%3A%2F%2FOrganization_Y%2FCS105%2Fgp-v2-activity%2F382a80f3f706441799e620417e60f5b6",
                "name": "Ten Timeless Tests",
                "object_map": {},
                "required_fields": [],
                "start": "2015-10-29T01:00:00Z",
                "uri": "http://lms.mcka.local/api/server/courses/Organization_Y/CS105/2018_T5/content/"
                       "i4x://Organization_Y/CS105/gp-v2-activity/382a80f3f706441799e620417e60f5b6",
                "valid_fields": None,
            }
        ],
       "course_id": "Organization_Y/CS105/2018_T5",
       "id": "i4x://Organization_Y/CS105/gp-v2-project/1b4fc43f58a14705bb6c4f0e68f4cbaa",
       "is_v2": True,
       "name": "Group Work",
       "vertical_id": "i4x://Organization_Y/CS105/vertical/52e720cef3594b79b3fd672f22054537"
    }
]
