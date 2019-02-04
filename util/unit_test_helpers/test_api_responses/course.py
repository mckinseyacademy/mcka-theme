import httpretty

from django.conf import settings

from api_client.course_api import COURSEWARE_API


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
        body=course_depth_5,
        status=200,
        content_type='application/json',
    )


course_depth_5 = '''{
    "category": "course",
    "end": null,
    "name": "ContentCohorting",
    "language": "en",
    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018",
    "due": null,
    "number": "COT101",
    "content": [
        {
            "category": "chapter",
            "name": "Just Discuss",
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/chapter/01b118e713fa47eb896a3da0ac244bf9",
            "due": null,
            "id": "i4x://CS101/ORG101/chapter/01b118e713fa47eb896a3da0ac244bf9",
            "start": "2018-01-01T00:00:00Z",
            "children": [
                {
                    "category": "sequential",
                    "name": "Subsection",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/sequential/6f42116e2cfc4720ad00eef6c7549b96",
                    "due": null,
                    "id": "i4x://CS101/ORG101/sequential/6f42116e2cfc4720ad00eef6c7549b96",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Unit",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/vertical/6449acfcb3074bfa9630df242dd5b1a4",
                            "due": null,
                            "id": "i4x://CS101/ORG101/vertical/6449acfcb3074bfa9630df242dd5b1a4",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "discussion",
                                    "name": "Discussion",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/discussion/2e2c1fd4ba12431bac64059a469f3fd9",
                                    "due": null,
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
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/sequential/196ee0fca26049fa919c93bfa7b2294a",
                    "due": null,
                    "id": "i4x://CS101/ORG101/sequential/196ee0fca26049fa919c93bfa7b2294a",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Unit",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34",
                            "due": null,
                            "id": "i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "poll",
                                    "name": "Poll",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/poll/c43aee476d204792b9cfdd677dca2a9a",
                                    "due": null,
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
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/chapter/c19dd6d1753d4714917a03d82f03064f",
            "due": null,
            "id": "i4x://CS101/ORG101/chapter/c19dd6d1753d4714917a03d82f03064f",
            "start": "2018-01-01T00:00:00Z",
            "children": [
                {
                    "category": "sequential",
                    "name": "Subsection",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/sequential/0060884182634d16bdbb92cb9adc97d0",
                    "due": null,
                    "id": "i4x://CS101/ORG101/sequential/0060884182634d16bdbb92cb9adc97d0",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Unit",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/vertical/5cef8c7ac4dd4782b58de04ade4cd511",
                            "due": null,
                            "id": "i4x://CS101/ORG101/vertical/5cef8c7ac4dd4782b58de04ade4cd511",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "pb-instructor-tool",
                                    "name": "Instructor Tool",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://CS101/ORG101/pb-instructor-tool/1ee9b473ff3b42d1a166a5dbaf8b4775",
                                    "due": null,
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
            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://COTORG/COT101/chapter/241059bb81994498938c243d639bf5e0",
            "due": null,
            "id": "i4x://COTORG/COT101/chapter/241059bb81994498938c243d639bf5e0",
            "start": "2018-01-01T00:00:00Z",
            "children": [
                {
                    "category": "sequential",
                    "name": "Assessment",
                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://COTORG/COT101/sequential/c25d548c50374946adcae20c10945fad",
                    "due": null,
                    "id": "i4x://COTORG/COT101/sequential/c25d548c50374946adcae20c10945fad",
                    "start": "2018-01-01T00:00:00Z",
                    "children": [
                        {
                            "category": "vertical",
                            "name": "Assessment",
                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://COTORG/COT101/vertical/1c987b91b368472cafb7fd372c294c1f",
                            "due": null,
                            "id": "i4x://COTORG/COT101/vertical/1c987b91b368472cafb7fd372c294c1f",
                            "start": "2018-01-01T00:00:00Z",
                            "children": [
                                {
                                    "category": "problem-builder",
                                    "name": "Problem Builder",
                                    "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://COTORG/COT101/problem-builder/28b51b543f5c42e8ad555b368a2f21eb",
                                    "due": null,
                                    "id": "i4x://COTORG/COT101/problem-builder/28b51b543f5c42e8ad555b368a2f21eb",
                                    "start": "2018-01-01T00:00:00Z",
                                    "children": [
                                        {
                                            "category": "pb-mcq",
                                            "name": "",
                                            "uri": "http://lms.mcka.local/api/server/courses/CS101/ORG101/2018/content/i4x://COTORG/COT101/pb-mcq/e07f2d1adfc246bcb7c4d78a46809e45",
                                            "due": null,
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
}'''  # NOQA
