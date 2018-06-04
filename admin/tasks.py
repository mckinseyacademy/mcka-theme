"""
Celery tasks related to admin app
"""
from collections import OrderedDict
from tempfile import TemporaryFile

from urlparse import urljoin

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.urlresolvers import reverse

from celery.decorators import task
from celery.utils.log import get_task_logger
from celery import states as celery_states
from celery.exceptions import Ignore
from api_client import course_api
from api_client import group_api
from api_client import user_api
from api_client.api_error import ApiError
from util.csv_helpers import CSVWriter
from util.s3_helpers import PrivateMediaStorageThroughApros
from util.email_helpers import send_html_email


from .controller import CourseParticipantStats

logger = get_task_logger(__name__)


@task(name='admin.course_participants_data_retrieval_task', max_retries=3, queue='high_priority')
def course_participants_data_retrieval_task(
        course_id, company_id, task_id, base_url, user_id,
        lesson_completions=False, retry_params=None
    ):
    """
    Retrieves course participants' data using API

    results are set in celery result backend, batch status is updated on each successful retrieval
    """

    additional_fields = ['grades', 'roles', 'organizations']

    if lesson_completions:
        additional_fields.append('lesson_completions')

    api_params = {
        'page': 1,
        'per_page': 200,
        'page_size': 200,
        'additional_fields': ",".join(additional_fields),
    }
    task_log_msg = "Participants data retrieval task for course: {}".format(course_id)
    storage_path = settings.EXPORT_STATS_DIR

    # for company, keep data retrieval to company participants
    if company_id:
        api_params.update({'organizations': company_id})
        storage_path += '/' + company_id
        task_log_msg += " and company: {}".format(company_id)

    participants_data = []
    fetched = 0

    course_participants_stats = CourseParticipantStats(
        course_id, base_url, CourseParticipantStats.participant_record_parser
    )

    # resume and persist existing data in case of retry
    if retry_params:
        api_params = retry_params.get('api_params', api_params)
        participants_data = retry_params.get('data', [])
        fetched = len(participants_data)

    logger.info('Starting - {}'.format(task_log_msg))

    while True:
        try:
            participants_stats = course_participants_stats.get_participants_data(api_params)
        except Exception as e:
            course_participants_data_retrieval_task.update_state(
                task_id=task_id, state=celery_states.RETRY,
            )
            logger.error('Failed retrieving data from Participants API - {}'.format(e.message))
            raise course_participants_data_retrieval_task.retry(
                exc=e, kwargs={
                    'course_id': course_id, 'company_id': company_id, 'base_url': base_url,
                    'retry_params': {'api_params': api_params, 'data': participants_data},
                }
            )

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

    groupworks, assessments, lesson_completions = OrderedDict(), OrderedDict(), OrderedDict()

    # custom processing is needed for groupworks and assessments data
    # as csv column names are also dynamic for them
    for participant in participants_data:
        for groupwork in participant.get('groupworks'):
            label = groupwork.get('label')
            key = 'GW_{}'.format(label)
            if key not in groupworks:
                groupworks[key] = _('Group Work: {label}').format(label=label)
            participant[key] = '{}%'.format(groupwork.get('percent'))

        for assessment in participant.get('assessments'):
            label = assessment.get('label')
            key = 'AS_{}'.format(label)
            if key not in assessments:
                assessments[key] = _('Assessment: {label}').format(label=label)
            participant[key] = '{}%'.format(assessment.get('percent'))

        for lesson_number, completion in sorted(participant.get('lesson_completions', {}).iteritems()):
            key = 'PRG_{}'.format(lesson_number)
            if key not in lesson_completions:
                lesson_completions[key] = _('Lesson {lesson_number} Progress').format(lesson_number=lesson_number)
            participant[key] = '{}%'.format(completion)

    fields = OrderedDict([
        ("Id", ("id", '')),
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
        ("Engagement", ("engagement", '')),
        ("Activation Link", ("activation_link", '')),
        ("Country", ("country", '')),
    ])

    # update fields with groupworks/assignments data
    for label, title in groupworks.items() + assessments.items() + lesson_completions.items():
        fields[title] = (label, '0%')

    file_name = '{}_user_stats.csv'.format(course_id.replace('/', '_'))

    try:
        temp_csv_file = TemporaryFile()
    except Exception as e:
        course_participants_data_retrieval_task.update_state(
            task_id=task_id, state=celery_states.FAILURE
        )
        logger.error('Failed creating temp CSV file - {}'.format(e.message))
        raise Ignore()
    else:
        writer = CSVWriter(temp_csv_file, fields, participants_data)
        writer.write_csv()
        temp_csv_file.seek(0)

    logger.info('Created temp CSV file - {}'.format(task_log_msg))

    # path is created as: /company_id/course_id/file_name
    storage_path = '{}/{}/{}'.format(storage_path, course_id.replace('/', '__'), file_name)
    storage = default_storage

    try:
        # use private s3 storage for export files
        if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
            storage = PrivateMediaStorageThroughApros()
        storage_path = storage.save(storage_path, ContentFile(temp_csv_file.read()))
    except Exception as e:
        course_participants_data_retrieval_task.update_state(
            task_id=task_id, state=celery_states.RETRY
        )
        logger.error('Failed saving CSV to S3 - {}'.format(e.message))
        raise course_participants_data_retrieval_task.retry(exc=e)
    else:
        logger.info('Saved CSV to S3 - {}'.format(task_log_msg))
        temp_csv_file.close()

    logger.info('Finished - {}'.format(task_log_msg))

    download_url = urljoin(
        base=base_url,
        url=reverse('private_storage', kwargs={'path': storage_path})
    )

    # invoke email send task
    export_stats_notification_email_task.delay(
        user_id, course_id, file_name, base_url, download_url
    )

    return download_url


@task(name='admin.export_stats_notification_email', max_retries=5)
def export_stats_notification_email_task(user_id, course_id, report_name, base_url, download_url):
    """
    Sends export stats completion notification email to admin
    created as a separate task to support retries
    """
    task_log_msg = "Export Stats notification email task for course: {}".format(course_id)
    logger.info('Starting - {}'.format(task_log_msg))

    mcka_logo = urljoin(
        base=base_url,
        url='/static/image/McKA_logoBLUE.png'
    )

    try:
        user_data = user_api.get_user(user_id).to_dict()
    except Exception as e:
        logger.error(
            'Failed retrieving Admin User info from API - {} - {}'
            .format(e.message, task_log_msg)
        )
        raise export_stats_notification_email_task.retry(exc=e)

    try:
        send_html_email(
            subject=_('Participant stats for {} is ready to download').format(course_id),
            to_emails=[user_data.get('email')], template_name='admin/export_stats_email_template',
            template_data={
                'first_name': user_data.get('first_name'),
                'download_link': download_url, 'support_email': settings.MCKA_SUPPORT_EMAIL,
                'report_name': report_name, 'mcka_logo_url': mcka_logo
            }
        )
        logger.info('Email successfully sent - {}'.format(task_log_msg))
    except Exception as e:
        logger.error('Failed sending download link email to Admin {} - {}'.format(e.message, task_log_msg))
        raise export_stats_notification_email_task.retry(exc=e)

    logger.info('Finished - {}'.format(task_log_msg))

    return True


@task(name='admin.course_notifications_data_retrieval_task', max_retries=3)
def participants_notifications_data_task(course_id, company_id, task_id, retry_params=None):
    """
    Retrieves course participants' notifications data using API
    """
    api_params = {
        'fields': 'id', 'page': 1,
        'per_page': 200, 'page_size': 200,
    }
    task_log_msg = "Notifications data retrieval task for course: {}".format(course_id)

    # for company, keep data retrieval to company participants
    if company_id:
        api_params.update({'organizations': company_id})
        task_log_msg += " and company: {}".format(company_id)

    participants_data = []
    fetched = 0

    # resume and persist existing data in case of retry
    if retry_params:
        api_params = retry_params.get('api_params', api_params)
        participants_data = retry_params.get('data', [])
        fetched = len(participants_data)

    logger.info('Starting - {}'.format(task_log_msg))

    while True:
        try:
            course_participants = course_api.get_course_details_users(course_id, api_params)
        except Exception as e:
            logger.error('Failed retrieving data from Course Participants API - {}'.format(e.message))
            raise participants_notifications_data_task.retry(
                exc=e, kwargs={
                    'course_id': course_id, 'company_id': company_id,
                    'retry_params': {'api_params': api_params, 'data': participants_data},
                }
            )

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
