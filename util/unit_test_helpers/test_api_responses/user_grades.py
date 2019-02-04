import httpretty

from django.conf import settings

from api_client.user_api import USER_API


def setup_user_gradebook_response(course_id, user_id):
    url = '{}/{}/{}/courses/{}/grades'.format(
        settings.API_SERVER_ADDRESS,
        USER_API,
        user_id,
        course_id
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=user_course_grade,
        status=200,
        content_type='application/json',
    )


user_course_grade = '''
{
    "current_grade": 0.4,
    "proforma_grade": 0.4,
    "courseware_summary": [
        {
            "display_name": "Just Discuss",
            "url_name": "01b118e713fa47eb896a3da0ac244bf9",
            "sections": [
                {
                    "url_name": "6f42116e2cfc4720ad00eef6c7549b96",
                    "display_name": "Subsection",
                    "graded": false,
                    "format": null,
                    "graded_total": [
                        0,
                        0,
                        true,
                        null
                    ],
                    "section_total": [
                        0,
                        0,
                        false,
                        null
                    ],
                    "due": null,
                    "location": "i4x://COTORG/COT101/sequential/6f42116e2cfc4720ad00eef6c7549b96"
                },
                {
                    "url_name": "196ee0fca26049fa919c93bfa7b2294a",
                    "display_name": "Poll",
                    "graded": false,
                    "format": null,
                    "graded_total": [
                        0,
                        0,
                        true,
                        null
                    ],
                    "section_total": [
                        0,
                        0,
                        false,
                        null
                    ],
                    "due": null,
                    "location": "i4x://COTORG/COT101/sequential/196ee0fca26049fa919c93bfa7b2294a"
                }
            ]
        },
        {
            "display_name": "Instructor Toolbar",
            "url_name": "c19dd6d1753d4714917a03d82f03064f",
            "sections": [
                {
                    "url_name": "0060884182634d16bdbb92cb9adc97d0",
                    "display_name": "Subsection",
                    "graded": false,
                    "format": null,
                    "graded_total": [
                        0,
                        0,
                        true,
                        null
                    ],
                    "section_total": [
                        0,
                        0,
                        false,
                        null
                    ],
                    "due": null,
                    "location": "i4x://COTORG/COT101/sequential/0060884182634d16bdbb92cb9adc97d0"
                }
            ]
        },
        {
            "display_name": "Scorm Handler",
            "url_name": "611cff0341e341788a86c518b937cbf8",
            "sections": [
                {
                    "url_name": "b52dc57bf57249b192e8b720481e7c5e",
                    "display_name": "Subsection",
                    "graded": false,
                    "format": null,
                    "graded_total": [
                        0,
                        0,
                        true,
                        null
                    ],
                    "section_total": [
                        0,
                        0,
                        false,
                        null
                    ],
                    "due": null,
                    "location": "i4x://COTORG/COT101/sequential/b52dc57bf57249b192e8b720481e7c5e"
                }
            ]
        },
        {
            "display_name": "Assesment",
            "url_name": "241059bb81994498938c243d639bf5e0",
            "sections": [
                {
                    "url_name": "c25d548c50374946adcae20c10945fad",
                    "display_name": "Assessment",
                    "graded": true,
                    "format": "Assessment",
                    "graded_total": [
                        5,
                        5,
                        true,
                        "2019-01-18T14:13:53.784015+00:00"
                    ],
                    "section_total": [
                        5,
                        5,
                        false,
                        "2019-01-18T14:13:53.784015+00:00"
                    ],
                    "due": null,
                    "location": "i4x://COTORG/COT101/sequential/c25d548c50374946adcae20c10945fad"
                }
            ]
        }
    ],
    "grade_summary": {
        "section_breakdown": [
            {
                "category": "Assessment",
                "label": "Assessment",
                "percent": 1,
                "detail": "Assessment = 100%",
                "prominent": true
            }
        ],
        "grade": null,
        "percent": 0.4,
        "grade_breakdown": {
            "Assessment": {
                "category": "Assessment",
                "percent": 0.4,
                "detail": "Assessment = 40.00% of a possible 40.00%"
            }
        }
    },
    "grading_policy": {
        "GRADE_CUTOFFS": {
            "Pass": 0.6
        },
        "GRADER": [
            {
                "min_count": 1,
                "weight": 0.4,
                "type": "Assessment",
                "drop_count": 0,
                "short_label": "Assessment"
            }
        ]
    }
}
'''
