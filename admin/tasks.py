"""
Celery tasks related to admin app
"""
from django.core.cache import cache

from celery.decorators import task
from celery.utils.log import get_task_logger

from api_client import course_api

from .controller import CourseParticipantStats
from .models import BatchOperationStatus


logger = get_task_logger(__name__)


@task(name='admin.course_participants_data_retrieval_task')
def course_participants_data_retrieval_task(course_id, company_id, task_id, base_url):
    """
    Retrieves course participants' data using API

    results are set in celery result backend, batch status is updated on each successful retrieval
    """
    api_params = {
        'page': 1, 'per_page': 100, 'page_size': 100,
        'additional_fields': "grades,roles,organizations",
    }
    task_log_msg = "Participants data retrieval task for course: {}".format(course_id)

    # for company, keep data retrieval to company participants
    if company_id:
        api_params.update({'organizations': company_id})
        task_log_msg += " and company: {}".format(company_id)

    participants_data = []
    fetched = 0

    course_participants_stats = CourseParticipantStats(
        course_id, base_url, CourseParticipantStats.participant_record_parser
    )
    batch_status = BatchOperationStatus.objects.create(task_key=task_id)

    logger.info('Starting - {}'.format(task_log_msg))

    while True:
        participants_stats = course_participants_stats.get_participants_data(api_params)
        participants_data.extend(participants_stats.get('results'))

        total = participants_stats.get('count')
        fetched += len(participants_stats.get('results'))
        percentage_fetched = (100.0 / (total or 1)) * fetched

        api_params['page'] += 1

        if batch_status is not None:
            batch_status.attempted = percentage_fetched  # attempted tracks percentage
            batch_status.save()

            logger.info(
                'Progress {}% - {}'
                .format(percentage_fetched, task_log_msg)
            )

        if not participants_stats.get('next'):
            break

    batch_status.succeded = 1
    batch_status.save()

    logger.info('Finished - {}'.format(task_log_msg))

    return participants_data


@task(name='admin.course_notifications_data_retrieval_task')
def participants_notifications_data_task(course_id, company_id, task_id):
    """
    Retrieves course participants' notifications data using API
    """
    api_params = {
        'fields': 'id', 'page': 1,
        'per_page': 100, 'page_size': 100,
    }
    task_log_msg = "Notifications data retrieval task for course: {}".format(course_id)

    # for company, keep data retrieval to company participants
    if company_id:
        api_params.update({'organizations': company_id})
        task_log_msg += " and company: {}".format(company_id)

    participants_data = []
    fetched = 0

    batch_status = BatchOperationStatus.objects.create(task_key=task_id)

    logger.info('Starting - {}'.format(task_log_msg))

    while True:
        course_participants = course_api.get_course_details_users(course_id, api_params)

        participants_data.extend(course_participants.get('results'))

        total = course_participants.get('count')
        fetched += len(course_participants.get('results'))
        percentage_fetched = (100.0 / (total or 1)) * fetched

        api_params['page'] += 1

        if batch_status is not None:
            batch_status.attempted = percentage_fetched  # attempted tracks percentage
            batch_status.save()

            logger.info(
                'Progress {}% - {}'
                .format(percentage_fetched, task_log_msg)
            )

        if not course_participants.get('next'):
            break

    batch_status.succeded = 1
    batch_status.save()

    logger.info('Finished - {}'.format(task_log_msg))

    return participants_data
