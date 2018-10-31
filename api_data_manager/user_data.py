import json

from django.conf import settings
from django.core.cache import cache

from lib.utils import DottableDict

from .common import DataManager
from .common_data import CommonDataManager, COMMON_DATA_PROPERTIES

USER_PROPERTIES = DottableDict(
    PREFERENCES='preferences',
    PROFILE='profile',
    GROUPS='groups',
    ORGANIZATIONS='organizations',
    COURSES='courses',
    USER_COURSE_DETAIL='user_course_detail',
    USER_COURSE_WORKGROUPS='user_course_workgroups',
)

GROUPS_SUB_TYPES = DottableDict(
    SERIES='series',
    PERMISSIONS='permission',
    REVIEW_ASSIGNMENTS='reviewassignment'
)


class UserDataManager(DataManager):
    cache_key_prefix = 'user'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('user_data')

    def __init__(self, user_id, identifiers=None):
        self.user_id = user_id
        self.cache_unique_identifier = '{}_{}'.format('_'.join(identifiers), user_id) if identifiers else user_id

    def delete_cached_data(self, property_name):
        if property_name == USER_PROPERTIES.USER_COURSE_WORKGROUPS:
            user_courses = self.get_cached_data(property_name=USER_PROPERTIES.COURSES)

            if user_courses is not None:
                user_courses = json.loads(user_courses)
                for course in user_courses:
                    cache_key = self.get_cache_key(
                        property_name=property_name,
                        identifier='{}_{}'.format(course.get('id'), self.user_id)
                    )
                    cache.delete(cache_key)

        if property_name == USER_PROPERTIES.GROUPS:
            # need to delete user course programs records as well
            user_courses = self.get_cached_data(property_name=USER_PROPERTIES.COURSES)
            if user_courses is not None:
                user_courses = json.loads(user_courses)
                group_name = GROUPS_SUB_TYPES.SERIES

                for course in user_courses:
                    cache_key = self.get_cache_key(
                        property_name='{}_{}'.format(property_name, group_name),
                        identifier='{}_{}'.format(course.get('id'), self.user_id)
                    )
                    cache.delete(cache_key)

            for group_key, group_name in GROUPS_SUB_TYPES.iteritems():
                cache_key = self.get_cache_key(property_name='{}_{}'.format(property_name, group_name))
                cache.delete(cache_key)

        super(UserDataManager, self).delete_cached_data(property_name)

    def get_basic_user_data(self):
        """
        Utility method for getting cache based common user data

        stores:
            courses
            current course
            current program
            organization
        """
        from api_client import user_api
        from admin.models import Program
        from courses.user_courses import CURRENT_COURSE_ID, CURRENT_PROGRAM_ID

        current_course = None
        current_program = Program.no_program()
        courses = user_api.get_user_courses(self.user_id)
        organizations = user_api.get_user_organizations(self.user_id)
        user_preferences = user_api.get_user_preferences(self.user_id)

        current_course_id = user_preferences.get(CURRENT_COURSE_ID, None)
        current_program_id = user_preferences.get(CURRENT_PROGRAM_ID, None)

        if current_program_id and current_program_id != Program.NO_PROGRAM_ID:
            program_courses_mapping = CommonDataManager().get_cached_data(
                COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING)

            if program_courses_mapping is not None:
                program_data = program_courses_mapping.get(int(current_program_id))
                if program_data:
                    current_program = Program(
                        dictionary={"id": program_data.get('id'), "name": program_data.get('name')}
                    )

        if current_course_id:
            for course in courses:
                if course.id == current_course_id:
                    current_course = course
        else:
            active_courses = [course for course in courses if course.is_active and course.started]
            if active_courses:
                current_course = active_courses[0]

        if not current_program and current_course:
            programs = Program.user_programs_with_course(
                self.user_id,
                current_course.id,
            )
            if programs:
                current_program = programs[0]

        return DottableDict(
            courses=courses,
            current_course=current_course,
            current_program=current_program,
            organization=organizations[0] if organizations else None,
        )
