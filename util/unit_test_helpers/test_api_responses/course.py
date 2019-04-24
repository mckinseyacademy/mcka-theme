# -*- coding: utf-8 -*-
import json
import httpretty
from urllib import urlencode

from django.conf import settings

from api_client.course_api import COURSEWARE_API, COURSE_COURSE_API, COURSE_BLOCK_API


def setup_course_response(course_id, username):
    url = '{}/{}/{}?depth={}{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        5,
        '&username={}'.format(username)
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_depth_5),
        status=200,
        content_type='application/json',
    )


def setup_get_course_details_users_response(course_id, qs_params=''):
    url = '{}/{}/{}/users?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params)
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_details_users),
        status=200,
        content_type='application/json',
    )


def setup_get_users_filtered_by_role_response(course_id):
    url = '{}/{}/{}/roles'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_roleset),
        status=200,
        content_type='application/json',
    )


def setup_course_overview_response(course_id):
    url = '{}/{}/{}/overview?parse=true'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=course_overview,
        status=200,
        content_type='application/json',
    )


def setup_course_list_response():
    url = '{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=course_list,
        status=200,
        content_type='application/json',
    )


def setup_course_v1_response(course_id):
    url = '{}/{}/{}/?'.format(
        settings.API_SERVER_ADDRESS,
        COURSE_COURSE_API,
        course_id
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=course_vi,
        status=200,
        content_type='application/json',
    )


def setup_get_course_blocks_responses(
    course_id,
    requested_fields,
    username=None,
    all_blocks=False,
    student_view_data=None,
    block_counts=None,
    depth=0,
    return_type='dict',
    block_types_filter=None,
    page_size=100,
):
    args = {
        'course_id': course_id,
        'requested_fields': requested_fields,
        'username': username,
        'all_blocks': all_blocks,
        'student_view_data': student_view_data,
        'block_counts': block_counts,
        'depth': depth,
        'return_type': return_type,
        'block_types_filter': block_types_filter,
    }
    params = {}
    for key in args:
        if args[key]:
            params[key] = args[key]

    url = '{}/{}/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSE_BLOCK_API,
        urlencode(params)
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(get_course_blocks(course_id)),
        status=200,
        content_type='application/json',
        match_querystring=True,
    )


def get_course_blocks(course_id):
    child_block_types = {
        'course': 'chapter',
        'chapter': 'sequential',
        'sequential': 'vertical',
        'vertical': 'poll',
    }

    def course_block(block_id, block_type, children=None, student_view_data=None):
        full_id = 'block-v1:{course_id}+type@{block_type}+block@{block_id}'.format(
            course_id=course_id, block_type=block_type, block_id=block_id
        )
        block = {
            'block_id': block_id,
            'id': full_id,
            'display_name': 'Block {block_id} of type {block_type}'.format(
                block_id=block_id, block_type=block_type
            ),
            'lms_web_url': '{lms_base_url}/courses/{course_id}/jump_to/{full_id}'.format(
                lms_base_url=settings.API_SERVER_ADDRESS,
                course_id=course_id, full_id=full_id,
            ),
            'student_view_url': '{lms_base_url}/xblock/{full_id}'.format(
                lms_base_url=settings.API_SERVER_ADDRESS, full_id=full_id,
            ),
            'type': block_type,
        }
        if children:
            block['children'] = [
                'block-v1:{course_id}+type@{block_type}+block@{block_id}'.format(
                    course_id=course_id,
                    block_type=child_block_types[block_type],
                    block_id=child_id
                ) for child_id in children
            ]
        if student_view_data:
            block['student_view_data'] = {
                'private_results': False,
                'max_submissions': 1,
                'question': 'Question {}'.format(student_view_data),
                'feedback': '',
                'answers': [
                    ["R", {"img": '', "img_alt": '', "label": "Red"}],
                    ["B", {"img": '', "img_alt": '', "label": "Blue"}],
                    ["G", {"img": '', "img_alt": '', "label": "Green"}],
                    ["O", {"img": '', "img_alt": '', "label": "Other"}]
                ]
            }
        return block

    return [course_block(*args, **kwargs) for (args, kwargs) in (
        (
            ('course', 'course'),
            {'children': ['chapter_block_1', 'الفصل_block_2']}
        ),
        (
            ('chapter_block_1', 'chapter'),
            {'children': ['sequential_block_1_1']}
        ),
        (
            ('الفصل_block_2', 'chapter'),
            {'children': ['تسلسلي_block_2_1']}
        ),
        (
            ('sequential_block_1_1', 'sequential'),
            {'children': ['vertical_block_1_1_1', 'vertical_block_1_1_2']}
        ),
        (
            ('تسلسلي_block_2_1', 'sequential'),
            {'children': ['عمودي_block_2_1_1']}
        ),
        (
            ('vertical_block_1_1_1', 'vertical'),
            {'children': ['poll_block_1_1_1_1', 'poll_block_1_1_1_2']}
        ),
        (
            ('vertical_block_1_1_2', 'vertical'),
            {'children': ['poll_block_1_1_2_1']}
        ),
        (
            ('عمودي_block_2_1_1', 'vertical'),
            {'children': ['poll_block_2_1_1_1']}
        ),
        (
            ('poll_block_1_1_1_1', 'poll'),
            {'student_view_data': '1.1.1.1'}
        ),
        (
            ('poll_block_1_1_1_2', 'poll'),
            {'student_view_data': '1.1.1.2'}
        ),
        (
            ('poll_block_1_1_2_1', 'poll'),
            {'student_view_data': '1.1.2.1'}
        ),
        (
            ('poll_block_1_2_1_1', 'poll'),
            {'student_view_data': '1.2.1.1'}
        ),
        (
            ('poll_block_2_1_1_1', 'poll'),
            {'student_view_data': '二.1.1.1'}
        ),
    )]


course_list = '''[
    {
        "id": "COTORG/COT101/2018_T1",
        "name": "ContentCohorting",
        "category": "course",
        "number": "COT101",
        "org": "COTORG",
        "uri": "http://lms.mcka.local/api/server/courses/COTORG/COT101/2018_T1",
        "course_image_url": "/c4x/COTORG/COT101/asset/images_course_image.jpg",
        "mobile_available": false,
        "due": null,
        "start": "2018-01-01T00:00:00Z",
        "end": null
    },
    {
        "id": "course-v1:edX+DemoX+Demo_Course",
        "name": "edX Demonstration Course",
        "category": "course",
        "number": "DemoX",
        "org": "edX",
        "uri": "http://lms.mcka.local/api/server/courses/course-v1:edX+DemoX+Demo_Course",
        "course_image_url": "/asset-v1:edX+DemoX+Demo_Course+type@asset+block@images_course_image.jpg",
        "mobile_available": false,
        "due": null,
        "start": "2019-02-05T05:00:00Z",
        "end": null
    }
]'''

course_vi = '''{
    "blocks_url": "http://lms.mcka.local/api/courses/v1/blocks/?course_id=COTORG%2FCOT101%2F2018_T1",
    "effort": null,
    "end": null,
    "enrollment_start": null,
    "enrollment_end": null,
    "id": "CCS101/ORG101/2018",
    "media": {
        "course_image": {
            "uri": "/c4x/COTORG/COT101/asset/images_course_image.jpg"
        },
        "course_video": {
            "uri": null
        },
        "image": {
            "raw": "http://lms.mcka.local/c4x/COTORG/COT101/asset/images_course_image.jpg",
            "small": "http://lms.mcka.local/c4x/COTORG/COT101/asset/images_course_image.jpg",
            "large": "http://lms.mcka.local/c4x/COTORG/COT101/asset/images_course_image.jpg"
        }
    },
    "name": "ContentCohorting",
    "number": "COT101",
    "org": "COTORG",
    "short_description": "",
    "start": "2018-01-01T00:00:00Z",
    "start_display": "Jan. 1, 2018",
    "start_type": "timestamp",
    "pacing": "instructor",
    "mobile_available": false,
    "hidden": false,
    "invitation_only": false,
    "course_id": "COTORG/COT101/2018_T1",
    "overview": ""
}'''  # NOQA

course_overview = '''{
    "sections": [
        {
            "class": "about",
            "attributes": {},
            "body": "<h2>About This Course</h2><p>Include your long course description here. The long course description should contain 150-400 words.</p><p>This is paragraph 2 of the long course description. Add more paragraphs as needed. Make sure to enclose them in paragraph tags.</p>"
        }
    ],
    "course_image_url": "/c4x/COTORG/COT101/asset/images_course_image.jpg",
    "course_video": ""
}'''  # NOQA


course_depth_5 = {
    "category": "course",
    "end": "null",
    "name": "ContentCohorting",
    "language": "en",
    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018",
    "due": "null",
    "number": "COT101",
    "content": [
        {
            "category": "chapter",
            "name": "Just Discuss",
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content"
                   "/i4x://CS101/ORG101/chapter/01b118e713fa47eb896a3da0ac244bf9",
            "due": "null",
            "id": "i4x://CS101/ORG101/chapter/01b118e713fa47eb896a3da0ac244bf9",
            "start": "2018-01-01T00:00:00Z",
            "children": [
                {
                    "category": "sequential",
                    "name": "Subsection",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                           "i4x://CS101/ORG101/sequential/6f42116e2cfc4720ad00eef6c7549b96",
                    "due": "null",
                    "id": "i4x://CS101/ORG101/sequential/6f42116e2cfc4720ad00eef6c7549b96",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Unit",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                   "i4x://CS101/ORG101/vertical/6449acfcb3074bfa9630df242dd5b1a4",
                            "due": "null",
                            "id": "i4x://CS101/ORG101/vertical/6449acfcb3074bfa9630df242dd5b1a4",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "discussion",
                                    "name": "Discussion",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                           "i4x://CS101/ORG101/discussion/2e2c1fd4ba12431bac64059a469f3fd9",
                                    "due": "null",
                                    "id": "i4x://CS101/ORG101/discussion/2e2c1fd4ba12431bac64059a469f3fd9",
                                    "start": "2018-01-01T00:00:00Z",
                                    "children": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "category": "sequential",
                    "name": "Poll",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                           "i4x://CS101/ORG101/sequential/196ee0fca26049fa919c93bfa7b2294a",
                    "due": "null",
                    "id": "i4x://CS101/ORG101/sequential/196ee0fca26049fa919c93bfa7b2294a",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Unit",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content"
                                   "/i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34",
                            "due": "null",
                            "id": "i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "poll",
                                    "name": "Poll",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                           "i4x://CS101/ORG101/poll/c43aee476d204792b9cfdd677dca2a9a",
                                    "due": "null",
                                    "id": "i4x://CS101/ORG101/poll/c43aee476d204792b9cfdd677dca2a9a",
                                    "start": "2018-01-01T00:00:00Z",
                                    "children": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "category": "chapter",
            "name": "Instructor Toolbar",
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                   "i4x://CS101/ORG101/chapter/c19dd6d1753d4714917a03d82f03064f",
            "due": "null",
            "id": "i4x://CS101/ORG101/chapter/c19dd6d1753d4714917a03d82f03064f",
            "start": "2018-01-01T00:00:00Z",
            "children": [
                {
                    "category": "sequential",
                    "name": "Subsection",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                           "i4x://CS101/ORG101/sequential/0060884182634d16bdbb92cb9adc97d0",
                    "due": "null",
                    "id": "i4x://CS101/ORG101/sequential/0060884182634d16bdbb92cb9adc97d0",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Unit",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                   "i4x://CS101/ORG101/vertical/5cef8c7ac4dd4782b58de04ade4cd511",
                            "due": "null",
                            "id": "i4x://CS101/ORG101/vertical/5cef8c7ac4dd4782b58de04ade4cd511",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "pb-instructor-tool",
                                    "name": "Instructor Tool",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                           "i4x://CS101/ORG101/pb-instructor-tool/1ee9b473ff3b42d1a166a5dbaf8b4775",
                                    "due": "null",
                                    "id": "i4x://CS101/ORG101/pb-instructor-tool/1ee9b473ff3b42d1a166a5dbaf8b4775",
                                    "start": "2018-01-01T00:00:00Z",
                                    "children": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "category": "chapter",
            "name": "Assesment",
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                   "i4x://COTORG/COT101/chapter/241059bb81994498938c243d639bf5e0",
            "due": "null",
            "id": "i4x://COTORG/COT101/chapter/241059bb81994498938c243d639bf5e0",
            "start": "2018-01-01T00:00:00Z",
            "children": [
                {
                    "category": "sequential",
                    "name": "Assessment",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                           "i4x://COTORG/COT101/sequential/c25d548c50374946adcae20c10945fad",
                    "due": "null",
                    "id": "i4x://COTORG/COT101/sequential/c25d548c50374946adcae20c10945fad",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Assessment",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                   "i4x://COTORG/COT101/vertical/1c987b91b368472cafb7fd372c294c1f",
                            "due": "null",
                            "id": "i4x://COTORG/COT101/vertical/1c987b91b368472cafb7fd372c294c1f",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "problem-builder",
                                    "name": "Problem Builder",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                           "i4x://COTORG/COT101/problem-builder/28b51b543f5c42e8ad555b368a2f21eb",
                                    "due": "null",
                                    "id": "i4x://COTORG/COT101/problem-builder/28b51b543f5c42e8ad555b368a2f21eb",
                                    "start": "2018-01-01T00:00:00Z",
                                    "children": [
                                        {
                                            "category": "pb-mcq",
                                            "name": "",
                                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
                                                   "i4x://COTORG/COT101/pb-mcq/e07f2d1adfc246bcb7c4d78a46809e45",
                                            "due": "null",
                                            "id": "i4x://COTORG/COT101/pb-mcq/e07f2d1adfc246bcb7c4d78a46809e45",
                                            "start": "2018-01-01T00:00:00Z",
                                            "children": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ],
    "start": "2018-01-01T00:00:00Z",
    "org": "COTORG",
    "id": "CS101/ORG101/2018",
    "resources": [
        {
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/"
        },
        {
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/groups/"
        },
        {
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/overview/"
        },
        {
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/updates/"
        },
        {
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/static_tabs/"
        },
        {
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/users/"
        }
    ],
    "course_image_url": "/c4x/CS101/ORG101/asset/images_course_image.jpg"
}  # NOQA

course_details_users = {
    'results': [
        {
            'id': 1,
            'username': 'Jane Doe',
            'is_active': True,
        }
    ],
    'next': ''
}

course_roleset = [
    {
        "role": "instructor",
        "id": 21893
    },
    {
        "role": "staff",
        "id": 21893
    },
    {
        "role": "assistant",
        "id": 8
    },
    {
        "role": "assistant",
        "id": 9
    }
]
