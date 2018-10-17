from api_client.json_object import JsonObject
from api_client.user_models import UserResponse


class CohortDiscussionSettings(JsonObject):
    """
    Data structure for cohort discussion settings.
    """
    required_fields = [
        'always_divide_inline_discussions',
        'available_division_schemes',
        'divided_inline_discussions',
        'division_scheme',
        'id',
        'divided_course_wide_discussions',
    ]


class Cohort(JsonObject):
    """
    Data structure for cohort.
    """
    required_fields = ['user_count', 'name', 'assignment_type', 'id']


class CohortUserUpdateResponse(JsonObject):
    object_map = {
        'preassigned': UserResponse,
        'added': UserResponse,
        'changed': UserResponse,
    }
    required_fields = [
        'preassigned',
        'added',
        'success',
        'unknown',
        'changed',
        'invalid',
        'present',
    ]
