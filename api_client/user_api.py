from json_object import JsonParser as JP, JsonObject
import user_models
from json_requests import GET, POST, DELETE, PUT

from django.conf import settings

AUTH_API = 'api/sessions'
USER_API = 'api/users'

def authenticate(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = POST('{}/{}/'.format(settings.API_SERVER_ADDRESS, AUTH_API), data)
    return JP.from_json(response.read(), user_models.AuthenticationResponse)

def get_user(user_id):
    response = GET('{}/{}/{}'.format(settings.API_SERVER_ADDRESS, USER_API, user_id))
    return JP.from_json(response.read(), user_models.UserResponse)

def delete_session(session_key):
    DELETE('{}/{}/{}'.format(settings.API_SERVER_ADDRESS, AUTH_API, session_key))

def register_user(user_hash):
    user_keys = ["username", "first_name", "last_name", "email", "password"]
    data = {user_key: user_hash[user_key] for user_key in user_keys}

    response = POST('{}/{}/'.format(settings.API_SERVER_ADDRESS, USER_API), data)
    return JP.from_json(response.read())

#imports for mocking here
import json

def fetch_current_course_for_user(user_id):
    fake_course = {
        "program_name": "McKinsey Management Program",
        "name": "Mastering Difficult Conversations",
        "lessons": [
            {
                "name": "Name of Lesson 1",
                "url": "course/DEF/lesson/ZYX",
                "is_released": True,
                "percent_complete": 100,
            },
            {
                "name": "Name of Lesson 2",
                "url": "course/DEF/lesson/YXW",
                "is_released": True,
                "percent_complete": 100,
                "modules": [
                    {
                        "name": "Lesson 2, Module 1",
                        "percent_complete": 100,
                    },
                    {
                        "name": "Lesson 2, Module 2",
                        "percent_complete": 100,
                    },
                    {
                        "name": "Lesson 2, Module 3",
                        "percent_complete": 100,
                    },
                    {
                        "name": "Lesson 2, Module 4",
                        "percent_complete": 80,
                    },
                    {
                        "name": "Lesson 2, Module 5",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 6",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 7",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 8",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 9",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 10",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 11",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 12",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 13",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 14",
                        "percent_complete": 0,
                    },
                ]
            },
            {
                "name": "Name of Lesson 3",
                "url": "course/DEF/lesson/XWV",
                "is_released": True,
                "percent_complete": 80,
                "modules": [
                    {
                        "name": "Lesson 2, Module 1",
                        "percent_complete": 100,
                    },
                    {
                        "name": "Lesson 2, Module 2",
                        "percent_complete": 100,
                    },
                    {
                        "name": "Lesson 2, Module 3",
                        "percent_complete": 100,
                    },
                    {
                        "name": "Lesson 2, Module 4",
                        "percent_complete": 80,
                    },
                    {
                        "name": "Lesson 2, Module 5",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 6",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 7",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 8",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 9",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 10",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 11",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 12",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 13",
                        "percent_complete": 0,
                    },
                    {
                        "name": "Lesson 2, Module 14",
                        "percent_complete": 0,
                    },
                ]
            },
            {
                "name": "Name of Lesson 4",
                "url": "course/DEF/lesson/WVU",
                "is_released": True,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 5",
                "url": "course/DEF/lesson/VUT",
                "is_released": True,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 6",
                "url": "course/DEF/lesson/UTS",
                "is_released": True,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 7",
                "url": "course/DEF/lesson/TSR",
                "is_released": True,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 8",
                "url": "course/DEF/lesson/SRQ",
                "is_released": False,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 9",
                "url": "course/DEF/lesson/RQP",
                "is_released": False,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 10",
                "url": "course/DEF/lesson/QPO",
                "is_released": False,
                "percent_complete": 0,
            },
            {
                "name": "Name of Lesson 11",
                "url": "course/DEF/lesson/PON",
                "is_released": False,
                "percent_complete": 0,
            },
        ],
        "last_lesson_index": 2,
        "last_tab_index": 1,
    }

    course = JsonObject(json.dumps(fake_course))

    course.current_lesson = course.lessons[2]
    course.current_lesson.current_module = course.lessons[2].modules[3]

    return course
