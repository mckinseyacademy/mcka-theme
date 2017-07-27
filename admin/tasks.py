"""
Celery tasks related to admin app
"""
from django.core.cache import cache

from celery import shared_task

from util.query_manager import get_object_or_none

from .controller import CourseParticipantStats
from .models import BatchOperationStatus


@shared_task(name="admin.download_participants_csv_data")
def course_participants_data_retrieval_task(course_id, task_id, base_url):
    """
    Retrieves course participants' data using API

    results are set in cache, batch status is updated on each successful retrieval
    """
    api_params = {
        'page': 1, 'per_page': 100, 'count': 0,
        'page_size': 100, 'additional_fields': "grades,roles,organizations",
    }

    participants_data = []
    fetched = 0

    course_participants_stats = CourseParticipantStats(course_id, base_url)
    batch_status = get_object_or_none(BatchOperationStatus, task_key=task_id)

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

        if not participants_stats.get('next'):
            break

    # cached for download csv request later
    cache.set('participants-list-' + batch_status.task_key, participants_data)

    batch_status.succeded = 1
    batch_status.save()
