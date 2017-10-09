"""
Celery tasks related to admin app
"""
from collections import OrderedDict

from django.core.files.storage import default_storage

from celery.decorators import task
from celery.utils.log import get_task_logger
from celery import states as celery_states

from api_client import course_api
from api_client import group_api
from api_client.api_error import ApiError
from util.csv_helpers import CSVWriter

from .controller import CourseParticipantStats

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

    logger.info('Starting - {}'.format(task_log_msg))

    while True:
        participants_stats = course_participants_stats.get_participants_data(api_params)
        participants_data.extend(participants_stats.get('results'))

        total = participants_stats.get('count')
        fetched += len(participants_stats.get('results'))
        percentage_fetched = (100.0 / (total or 1)) * fetched

        course_participants_data_retrieval_task.update_state(
            task_id=task_id, state='PROGRESS', meta={'percentage': int(percentage_fetched)})

        api_params['page'] += 1

        logger.info(
            'Progress {}% - {}'
            .format(percentage_fetched, task_log_msg)
        )

        if not participants_stats.get('next'):
            break

    groupworks, assesments = OrderedDict(), OrderedDict()

    # custom processing is needed for groupworks and assesments data
    # as csv column names are also dynamic for them
    for participant in participants_data:
        for groupwork in participant.get('groupworks'):
            label = groupwork.get('label')
            key = 'GW_{}'.format(label)

            if key not in groupworks:
                groupworks[key] = 'Group Work: ' + label

            participant[key] = '{}%'.format(groupwork.get('percent'))

        for assesment in participant.get('assessments'):
            label = assesment.get('label')
            key = 'AS_{}'.format(label)

            if key not in assesments:
                assesments[key] = 'Assessment: ' + label

            participant[key] = '{}%'.format(assesment.get('percent'))

    fields = OrderedDict([
        ("ID", ("id", '')),
        ("First name", ("first_name", '')),
        ("Last name", ("last_name", '')),
        ("Username", ("username", '')),
        ("Email", ("email", '')),
        ("Company", ("organizations_display_name", '')),
        ("Status", ("custom_user_status", '')),
        ("Activated", ("custom_activated", '')),
        ("Last login", ("custom_last_login", '')),
        ("Progress", ("progress", '')),
        ("Proficiency", ("proficiency", '')),
        ("Activation Link", ("activation_link", '')),
        ("Country", ("country", '')),
    ])

    # update fields with groupworks/assignments data
    for label, title in (groupworks.items() + assesments.items()):
        fields.update({title: (label, '0%')})

    file_path = 'csv_exports/{}_user_stats.csv'.format(task_id)

    try:
        csv_file = default_storage.open(file_path, 'w')
    except:
        course_participants_data_retrieval_task.update_state(
            task_id=task_id, state=celery_states.FAILURE
        )
    else:
        writer = CSVWriter(csv_file, fields, participants_data)
        writer.write_csv()

        file_path = default_storage.url(file_path)

        csv_file.close()

    logger.info('Finished - {}'.format(task_log_msg))

    return file_path


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

    logger.info('Starting - {}'.format(task_log_msg))

    while True:
        course_participants = course_api.get_course_details_users(course_id, api_params)

        participants_data.extend(course_participants.get('results'))

        total = course_participants.get('count')
        fetched += len(course_participants.get('results'))
        percentage_fetched = (100.0 / (total or 1)) * fetched

        participants_notifications_data_task.update_state(
            task_id=task_id, state='PROGRESS', meta={'percentage': int(percentage_fetched)})

        api_params['page'] += 1

        logger.info(
            'Progress {}% - {}'
            .format(percentage_fetched, task_log_msg)
        )

        if not course_participants.get('next'):
            break

    logger.info('Finished - {}'.format(task_log_msg))

    return participants_data


@task(name='admin.users_program_association_task')
def users_program_association_task(program_id, user_ids, task_id):
    """
    Associate users with a program

    Returns:
        (dict): total and successfully added users
    """
    total = len(user_ids)
    added = 0
    failed = 0

    for user_id in user_ids:
        try:
            group_api.add_user_to_group(user_id, program_id)
            added += 1
        except ApiError as e:
            failed += 1
        finally:
            percentage = (100.0 / (total or 1)) * (added + failed)

            # ToDo: Look into updating progress in batches to
            # reduce DB hits for state updates
            users_program_association_task.update_state(
                task_id=task_id, state='PROGRESS', meta={'percentage': int(percentage)}
            )

    return {'successful': added, 'total': total}
