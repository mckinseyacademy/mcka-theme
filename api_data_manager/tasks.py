from collections import defaultdict

from django.conf import settings

from celery.utils.log import get_task_logger
from celery.decorators import task

from courses.models import FeatureFlags
from courses.course_tree_builder import CourseTreeBuilder
from api_client import group_api
from api_client import mobileapp_api
from api_client import organization_api
from api_data_manager.common_data import CommonDataManager, COMMON_DATA_PROPERTIES

from .course_data import CourseDataManager, COURSE_PROPERTIES

logger = get_task_logger(__name__)


@task
def build_common_data_cache():
    """
    Builds cache for common app data &
    for courses marked for enhanced caching
    """
    cache_program_courses_mapping.delay()
    cache_permission_groups.delay()
    cache_companion_app_courses.delay()

    enhanced_course_caching_task.delay()


@task(max_retries=3)
def cache_program_courses_mapping():
    common_data_manager = CommonDataManager()

    task_log_msg = "Build common data cache task"

    logger.info('{} - Starting'.format(task_log_msg))

    logger.info('{} - Building program-course mapping'.format(task_log_msg))

    try:
        all_programs = group_api.get_groups_of_type('series')
    except Exception as e:
        logger.error('{} - Exception retrieving programs list - {}'.format(task_log_msg, e.message))
        raise cache_program_courses_mapping.retry(exc=e)

    program_courses_mapping = defaultdict(dict)

    for program in all_programs:
        try:
            program_courses = group_api.get_courses_in_group(program.id)
        except Exception as e:
            logger.error(
                '{} - Exception retrieving program `{}` courses - SKIPPING - {}'
                .format(task_log_msg, program.id, e.message)
            )
        else:
            program_courses_mapping[program.id] = {'name': program.name, 'courses': program_courses}

    logger.info('{} - Completed building program-course mapping'.format(task_log_msg))

    common_data_manager.set_cached_data(
        COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING,
        data=program_courses_mapping
    )


@task
def cache_permission_groups():
    common_data_manager = CommonDataManager()
    task_log_msg = "Permission groups task"

    logger.info('{} -  Starting'.format(task_log_msg))

    try:
        permission_groups = group_api.get_groups_of_type('permission')
    except Exception as e:
        logger.error('{} - Exception retrieving permissions groups - {}'.format(task_log_msg, e.message))
    else:
        permission_groups_map = {permission_group.name: permission_group.id for permission_group in permission_groups}
        common_data_manager.set_cached_data(
            property_name=COMMON_DATA_PROPERTIES.PERMISSION_GROUPS,
            data=permission_groups_map
        )
        logger.info('{} - Completed retrieving permissions groups'.format(task_log_msg))

    return True


@task
def cache_companion_app_courses():
    common_data_manager = CommonDataManager()
    task_log_msg = "Companion App courses task"

    logger.info('{} - Starting'.format(task_log_msg))

    try:
        companion_app = mobileapp_api.get_mobile_apps({"app_name": "LBG"})
    except Exception as e:
        logger.error('{} - Exception retrieving companion mobile apps - {}'.format(task_log_msg, e.message))
    else:
        companion_app_orgs = companion_app['results'][0]['organizations'] if companion_app.get('results') else []
        companion_app_courses = []
        # get all the courses of companion app
        for org_id in companion_app_orgs:
            try:
                org_companion_app_courses = organization_api.get_organizations_courses(org_id)
            except Exception as e:
                logger.error('{} - Exception retrieving organization courses - {}'.format(task_log_msg, e.message))
            else:
                companion_app_courses.extend(org_companion_app_courses)

        # get the mobile available courses of companion app
        companion_app_courses_id = [course['id'] for course in companion_app_courses if course['mobile_available']]

        common_data_manager.set_cached_data(
            COMMON_DATA_PROPERTIES.COMPANION_APP_COURSES,
            data=companion_app_courses_id
        )
        logger.info('{} - Completed retrieving companion app courses'.format(task_log_msg))

    return True


@task
def enhanced_course_caching_task():
    """
    Builds course tree in advance for large cohort courses

    courses marked as `enhanced_caching` in
    course meta data are picked up
    """
    task_log_msg = "Course Tree prefetch task"
    logger.info('{} - Starting'.format(task_log_msg))

    course_ids = FeatureFlags.objects.filter(enhanced_caching=True)\
        .values_list('course_id', flat=True)

    success_ids = []

    logger.info('{} - Total courses with enhanced caching: {}'.format(task_log_msg, len(course_ids)))

    for course_id in course_ids:
        try:
            course = CourseTreeBuilder(course_id=course_id, request=None)\
                .get_processed_course_static_data()
        except Exception as e:
            logger.error('{} - Exception retrieving `{}` course tree data - {}'.format(
                task_log_msg, course_id, e.message
            ))
        else:
            course_data_manager = CourseDataManager(course_id=course_id)
            course_data_manager.set_cached_data(
                property_name=COURSE_PROPERTIES.PREFETCHED_COURSE_OBJECT,
                data=course,
                expiry_time=settings.CACHE_TIMEOUTS.get('prefetched_course_data',
                                                        settings.DEFAULT_CACHE_TIMEOUT)
            )
            success_ids.append(course_id)

    logger.info('{} - Successfully cached `{}` courses out of `{}`'
                .format(task_log_msg, len(success_ids), len(course_ids)))

    return True
