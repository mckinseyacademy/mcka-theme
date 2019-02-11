from celery.utils.log import get_task_logger
from django.dispatch import Signal, receiver

from .common_data import CommonDataManager, COMMON_DATA_PROPERTIES
from .course_data import CourseDataManager
from .group_data import GroupDataManager
from .user_data import UserDataManager

user_data_updated = Signal(providing_args=['user_ids', 'data_type'])
group_data_updated = Signal(providing_args=['group_ids', 'data_type'])
course_data_updated = Signal(providing_args=['course_ids', 'data_type'])
common_data_updated = Signal(providing_args=['data_type'])

logger = get_task_logger(__name__)


@receiver(user_data_updated)
def user_data_updated_handler(sender, *args, **kwargs):
    user_ids = kwargs.get('user_ids')
    user_property = kwargs.get('data_type')

    for user_id in user_ids:
        data_manager = UserDataManager(user_id=user_id)
        data_manager.delete_cached_data(user_property)


@receiver(course_data_updated)
def course_data_updated_handler(sender, *args, **kwargs):
    course_ids = kwargs.get('course_ids')
    course_property = kwargs.get('data_type')

    for course_id in course_ids:
        data_manager = CourseDataManager(course_id=course_id)
        data_manager.delete_cached_data(course_property)


@receiver(group_data_updated)
def group_data_updated_handler(sender, *args, **kwargs):
    group_ids = kwargs.get('group_ids')
    user_property = kwargs.get('data_type')

    for group_id in group_ids:
        data_manager = GroupDataManager(group_id=group_id)
        data_manager.delete_cached_data(user_property)


@receiver(common_data_updated)
def common_data_updated_handler(sender, *args, **kwargs):
    common_data_manager = CommonDataManager()
    common_data_property = kwargs.get('data_type')

    # update cached data - required for data integrity
    if common_data_property == COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING:
        group_id = kwargs.get('data_changed', {}).get('group_id')
        program_courses_mapping = common_data_manager.get_cached_data(
            property_name=COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING
        )

        if group_id and (program_courses_mapping is not None):
            from admin.models import Program

            logger.info('Program-Course Mapping changed for Program {}, updating cached data'.format(group_id))

            try:
                program = Program.fetch(group_id)
                program_courses = program.fetch_courses()
            except Exception as e:
                logger.error('Exception retrieving program for updating Program Course Mapping cache - {} - Skipping'
                             .format(e.message))
            else:
                program_courses_mapping[group_id] = {'name': program.name, 'courses': program_courses}

                common_data_manager.set_cached_data(
                    COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING,
                    data=program_courses_mapping
                )

                logger.info('Program-Course Mapping successfully updated for Program {}'.format(group_id))
