"""
Celery tasks related to admin app
"""
from django.core.cache import cache

from celery.decorators import task
from celery.utils.log import get_task_logger

from .controller import CourseParticipantStats
from .models import BatchOperationStatus


logger = get_task_logger(__name__)


@task(name='admin.course_participants_data_retrieval_task')
def course_participants_data_retrieval_task(course_id, task_id, base_url):
    """
    Retrieves course participants' data using API

    results are set in cache, batch status is updated on each successful retrieval
    """
    api_params = {
        'page': 1, 'per_page': 100, 'page_size': 100,
        'additional_fields': "grades,roles,organizations",
    }

    participants_data = []
    fetched = 0

    course_participants_stats = CourseParticipantStats(
        course_id, base_url, CourseParticipantStats.participant_record_parser
    )
    batch_status = BatchOperationStatus.objects.create(task_key=task_id)

    logger.info('Starting - Participants data retrieval task for course: {}'.format(course_id))

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
                'Progress {}% - Participants data retrieval task for course: {}'
                .format(percentage_fetched, course_id)
            )

        if not participants_stats.get('next'):
            break

    batch_status.succeded = 1
    batch_status.save()

    logger.info('Finished - Participants data retrieval task for course: {}'.format(course_id))

    return participants_data
