# -*- coding: utf-8 -*-
import httpretty

from django.conf import settings

from api_client.course_api import COURSEWARE_API


def setup_course_tabs_response(course_id):
    url = '{}/{}/{}/static_tabs'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
    )

    tab_url_estimated = '{}/{}/{}/static_tabs/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        '0a0abc707b7c4a6d926dc1ea6c4e6927',
    )

    tab_url_lesson = '{}/{}/{}/static_tabs/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        'b8c40111aaa2402cabefd79da6fd8e4d',
    )

    tab_url_resources = '{}/{}/{}/static_tabs/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        '62fb4db096ec42688ad1705d3f6999c1',
    )

    httpretty.register_uri(
        httpretty.GET,
        tab_url_estimated,
        body=course_tab_estimated_times,
        status=200,
        content_type='application/json',
    )

    httpretty.register_uri(
        httpretty.GET,
        tab_url_lesson,
        body=course_tab_lesson,
        status=200,
        content_type='application/json',
    )

    httpretty.register_uri(
        httpretty.GET,
        tab_url_resources,
        body=course_tab_resources,
        status=200,
        content_type='application/json',
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=course_tabs_with_details,
        status=200,
        content_type='application/json',
    )


course_tabs_with_details = '''{
    "tabs": [
        {
            "id": "62fb4db096ec42688ad1705d3f6999c1",
            "name": "Resources",
            "content": "<h1>Resources</h1>"
        },
        {
            "id": "0a0abc707b7c4a6d926dc1ea6c4e6927",
            "name": "Estimated Time",
            "content": "<p>est. time 60 min\\nest. time 85 min\\nest. time 40 min\\nest. time 30 min\\nest. time 40 min\\nest. time 40 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min</p>"
        },
        {
            "id": "b8c40111aaa2402cabefd79da6fd8e4d",
            "name": "Lesson1",
            "content": "<p>est. time 60 min\\nest. time 85 min\\nest. time 40 min\\nest. time 30 min\\nest. time 40 min\\nest. time 40 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min</p>"
        }
    ]
}'''  # NOQA


course_tab_estimated_times = '''{
    "id": "0a0abc707b7c4a6d926dc1ea6c4e6927",
    "name": "Estimated Time",
    "content": "<p>est. time 60 min\\nest. time 85 min\\nest. time 40 min\\nest. time 30 min\\nest. time 40 min\\nest. time 40 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min</p>"
}'''  # NOQA

course_tab_resources = '''{
    "id": "62fb4db096ec42688ad1705d3f6999c1",
    "name": "Resources",
    "content": "<p></p>\n<table style=\"border: none;\">\n<tbody>\n<tr>\n<td width=\"120\"><img src=\"/c4x/XblockORG/Xblock101/asset/Resources_page_icon.png\" /></td>\n<td width=\"600\">\n<div id=\"iguide\" class=\"label-5\">Jump to section:</div>\n<h2><a href=\"#iguide\"><i class=\"fa fa-fw\"></i><i class=\"fa fa-level-down\"></i> Informational guides</a></h2>\n<h2><a href=\"#takeaways\"><i class=\"fa fa-fw\"></i><i class=\"fa fa-level-down\"></i> Key takeaways, frameworks, and videos</a></h2>\n<h2><a href=\"#scontent\"><i class=\"fa fa-fw\"></i><i class=\"fa fa-level-down\"></i> Supplementary content</a></h2>\n</td>\n</tr>\n</tbody>\n</table>\n<hr />\n<p></p>\n"
}'''  # NOQA

course_tab_lesson = '''{
    "id": "b8c40111aaa2402cabefd79da6fd8e4d",
    "name": "Lesson1",
    "content": "<p>est. time 60 min\\nest. time 85 min\\nest. time 40 min\\nest. time 30 min\\nest. time 40 min\\nest. time 40 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min\\nest. time 30 min</p>"
}''' # NOQA
