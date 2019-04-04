"""
Celery tasks related to admin app
"""
import math
import os
import json
import hashlib
import time

import six
from collections import OrderedDict
from multiprocessing.pool import ThreadPool
from tempfile import TemporaryFile
from datetime import timedelta
from urlparse import urljoin

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from celery.decorators import task
from celery.utils.log import get_task_logger
from celery import states as celery_states
from celery.exceptions import Ignore, MaxRetriesExceededError, Reject, InvalidTaskError

from accounts.helpers import get_organization_by_user_email
from api_client import course_api, organization_api
from api_client import group_api
from api_client import instructor_api
from api_client import user_api
from api_client.api_error import ApiError
from api_client.cohort_api import add_cohort_for_course
from api_client.user_api import get_users
from util.csv_helpers import CSVWriter, create_and_store_csv_file
from util.s3_helpers import PrivateMediaStorageThroughApros, get_storage, get_path
from util.email_helpers import send_html_email

from admin.models import LearnerDashboardTile, AdminTask
from accounts.models import UserActivation
from accounts.helpers import create_activation_url
from courses.controller import strip_tile_link, get_course_object, update_progress

from .controller import (
    enroll_participants,
    process_line_register_participants_csv,
    process_line_enroll_participants_csv,
    build_student_list_from_file,
    create_update_delete_manager,
    validate_participant_and_manager_records,
    validate_company_field,
    update_company_field_for_users,
    CourseParticipantStats,
    ProblemReportPostProcessor,
    get_emails_from_csv,
    delete_company_data)
from .models import UserRegistrationError, UserRegistrationBatch


logger = get_task_logger(__name__)
DELETE_PARTICIPANTS_DIR = 'delete_participant_files'
IMPORT_PARTICIPANTS_DIR = 'import_participant_files'


@task(name='admin.course_participants_data_retrieval_task', max_retries=3, queue='high_priority')
def course_participants_data_retrieval_task(course_id, company_id, task_id, base_url, user_id,
                                            lesson_completions=False, retry_params=None
                                            ):
    """
    Retrieves course participants' data using API

    results are set in celery result backend, batch status is updated on each successful retrieval
    """

    additional_fields = ['grades', 'roles', 'organizations', 'progress']

    cohorts_enabled = course_api.get_course_cohort_settings(course_id).is_cohorted

    if cohorts_enabled:
        additional_fields.append('course_groups')

    if lesson_completions:
        additional_fields.append('lesson_completions')

    api_params = {
        'page': 1,
        'per_page': settings.MAX_USERS_PER_PAGE,
        'page_size': settings.MAX_USERS_PER_PAGE,
        'additional_fields': ",".join(additional_fields),
        # Profile images take a long time to serialize, and we don't need them.
        'exclude_fields': "profile_image",
    }
    task_log_msg = "Participants data retrieval task for course: " \
                   "`{}`, triggered by user `{}`".format(course_id, user_id)

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

            try:
                raise course_participants_data_retrieval_task.retry(
                    kwargs={
                        'course_id': course_id, 'company_id': company_id, 'base_url': base_url,
                        'user_id': user_id, 'lesson_completions': lesson_completions,
                        'retry_params': {'api_params': api_params, 'data': participants_data},
                    }
                )
            except (MaxRetriesExceededError, Reject) as e:
                # exit with a failure email on reject/max-retries
                if isinstance(e, MaxRetriesExceededError):
                    logger.error('Max retires reached - EXITING - {}'.format(task_log_msg))
                else:
                    logger.error('Retry rejected with error `{}` - EXITING - {}'.format(e.reason, task_log_msg))

                send_export_stats_status_email(
                    user_id=user_id, course_id=course_id,
                    report_name='', base_url=base_url,
                    download_url='', report_succeeded=False,
                )

                raise

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

    groupworks, assessments, lesson_completions, attributes = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()

    # custom processing is needed for groupworks and assessments data
    # as csv column names are also dynamic for them
    for participant in participants_data:
        if company_id:
            for field in participant.get('attributes'):
                attribute_key = field.get('key')
                if attribute_key:
                    attributes[attribute_key] = field.get('label', '')
                    participant[attribute_key] = field.get('value', '')

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

        if cohorts_enabled:
            course_groups = participant.get('course_groups')
            participant['course_group'] = course_groups[0] if course_groups else '-'

    fields = OrderedDict([
        ("Id", ("id", '')),
        ("First name", ("first_name", '')),
        ("Last name", ("last_name", '')),
        ("Username", ("username", '')),
        ("Email", ("email", '')),
        ("Company", ("organizations_display_name", '')),
    ] + [(item_label, (item_key, '')) for item_key, item_label in attributes.items()] + [
        ("Status", ("custom_user_status", '')),
        ("Activated", ("custom_activated", '')),
        ("Last login", ("custom_last_login", '')),
        ("Progress", ("progress", '')),
        ("Proficiency", ("proficiency", '')),
        ("Engagement", ("engagement", '')),
        ("Activation Link", ("activation_link", '')),
        ("Country", ("country", '')),
    ])

    if cohorts_enabled:
        fields['Course group'] = ("course_group", '')

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

    send_export_stats_status_email(
        user_id=user_id, course_id=course_id,
        report_name=file_name, base_url=base_url,
        download_url=download_url, report_succeeded=True,
    )

    return download_url


def send_bulk_fields_update_email(
        user_id, total_records, record_count, errors, base_url
):
    """ Send report of bulk company fields update on user's email """
    subject = _('Report for bulk update')
    template = 'admin/bulk_fields_update_report_email.haml'
    user_detail = user_api.get_user(user_id).to_dict()
    mcka_logo = urljoin(
        base=base_url,
        url='/static/image/mcka_email_logo.png'
    )

    send_html_email(
        subject=subject,
        to_emails=[user_detail.get('email')], template_name=template,
        template_data={
            'first_name': user_detail.get('first_name'), 'total_records': total_records,
            'success_count': record_count, 'failed_count': (total_records-record_count),
            'errors': errors, 'support_email': settings.MCKA_SUPPORT_EMAIL,
            'mcka_logo_url': mcka_logo,
        }
    )


def send_export_stats_status_email(
        user_id, course_id, report_name, base_url,
        download_url, report_succeeded=True,
):
    """
    Invokes notification email task
    """
    if report_succeeded:
        subject = _('Participant stats for {} is ready to download').format(course_id)
        email_template = 'admin/export_stats_email_template.haml'
    else:
        subject = _('Participant stats for {} did not generate').format(course_id)
        email_template = 'admin/export_stats_failure_email_template.haml'
        # create admin/course details url
        download_url = urljoin(
            base=base_url,
            url=reverse('course_details', kwargs={'course_id': course_id})
        )

    export_stats_status_email_task.delay(
        user_id=user_id, course_id=course_id,
        report_name=report_name, base_url=base_url, download_url=download_url,
        subject=subject, template=email_template,
    )


@task(name='admin.send_email')
def send_email(subject, email_template, template_data, user_emails, task_log_msg):
    """
    Sends email and logs it.
    :param user_emails: `list` of users to whom the message will be sent.
    """
    logger.info('Sending notification email - {}'.format(task_log_msg))

    try:
        send_html_email(
            subject=subject,
            to_emails=user_emails, template_name=email_template,
            template_data=template_data,
        )
    except Exception as e:
        logger.error('Failed sending notification email to Admin {} - {}'.format(e.message, task_log_msg))
        raise

    logger.info('Email successfully sent - {}'.format(task_log_msg))


@task(name='admin.export_stats_notification_email', max_retries=5)
def export_stats_status_email_task(
        user_id, course_id, report_name,
        base_url, download_url,
        subject, template,
):
    """
    Sends export stats notification email to admin
    created as a separate task to support retries
    """
    task_log_msg = "Export Stats notification email task for course:" \
                   " `{}` and user `{}`".format(course_id, user_id)

    logger.info('Starting - {}'.format(task_log_msg))

    mcka_logo = urljoin(
        base=base_url,
        url='/static/image/mcka_email_logo.png'
    )

    try:
        user_data = user_api.get_user(user_id).to_dict()
    except Exception as e:
        logger.error(
            'Failed retrieving Admin User info from API - {} - {}'
            .format(e.message, task_log_msg)
        )
        raise export_stats_status_email_task.retry(exc=e)

    try:
        send_html_email(
            subject=subject,
            to_emails=[user_data.get('email')], template_name=template,
            template_data={
                'first_name': user_data.get('first_name'),
                'download_link': download_url, 'support_email': settings.MCKA_SUPPORT_EMAIL,
                'report_name': report_name, 'mcka_logo_url': mcka_logo, 'course_id': course_id,
            }
        )
        logger.info('Email successfully sent - {}'.format(task_log_msg))
    except Exception as e:
        logger.error('Failed sending notification email to Admin {} - {}'.format(e.message, task_log_msg))
        raise export_stats_status_email_task.retry(exc=e)

    logger.info('Finished - {}'.format(task_log_msg))

    return True


@task(name='admin.course_notifications_data_retrieval_task', max_retries=3)
def participants_notifications_data_task(course_id, company_id, task_id, retry_params=None):
    """
    Retrieves course participants' notifications data using API
    """
    api_params = {
        'fields': 'id',
        'page': 1,
        'per_page': 1000,
        'page_size': 1000,
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
    task_log_msg = "User Program Association task for program: {}".format(program_id)

    total = len(user_ids)
    added = 0
    failed = 0
    batch_size = 100

    logger.info('Attempting to associate {} users - {}'.format(total, task_log_msg))

    for i in xrange(0, total, batch_size):
        user_ids_batch = user_ids[i:i+batch_size]

        try:
            group_api.add_users_to_group(user_ids_batch, program_id)
            added += len(user_ids_batch)
        except ApiError as e:
            logger.error('Failed adding users batch to group {} - {}'.format(e.message, task_log_msg))
            failed += len(user_ids_batch)
        finally:
            percentage = (100.0 / (total or 1)) * (added + failed)

            # ToDo: Look into updating progress in batches to
            # reduce DB hits for state updates
            users_program_association_task.update_state(
                task_id=task_id, state='PROGRESS', meta={'percentage': int(percentage)}
            )

    logger.info('Associated {} of {} users - {}'.format(added, total, task_log_msg))

    return {'successful': added, 'total': total}


@task(name='admin.import_participants_task', queue='high_priority')
def import_participants_task(user_id, base_url, file_url, is_internal_admin, registration_batch_id, register):
    """
    Processes a CSV file of participants.

    :param register: if `True`, new users will be created and enrolled, otherwise existing users will be enrolled
    """
    task_log_msg = "Import Participants task"

    logger.info('Started - {}'.format(task_log_msg))

    storage = get_storage(secure=True)
    file_path = get_path(file_url)

    try:
        file_stream = storage.open(file_path)
    except Exception as e:
        logger.error('{} - Failed to open file with path: {}'.format(task_log_msg, file_path))
        raise
    else:
        logger.info('Successfully opened CSV file - {}'.format(task_log_msg))

    parse_method = process_line_register_participants_csv if register else process_line_enroll_participants_csv

    user_list = build_student_list_from_file(file_stream, parse_method=parse_method)
    clean_user_list, unclean_user_list, user_registration_errors = [], [], []

    registration_batch = UserRegistrationBatch.objects.get(id=registration_batch_id)
    for user_info in user_list:
        if "error" in user_info:
            try:
                user_data = json.dumps(user_info)
            except (TypeError, ValueError):
                user_data = json.dumps({})

            unclean_user_list.append(user_info)
            user_registration_errors.append(
                UserRegistrationError(
                    error=user_info.get('error'),
                    task_key=registration_batch.task_key,
                    user_email=user_info.get('email'),
                    user_data=user_data
                )
            )
        else:
            clean_user_list.append(user_info)

    UserRegistrationError.objects.bulk_create(user_registration_errors)
    registration_batch.attempted = len(user_list)
    registration_batch.failed += len(user_registration_errors)
    registration_batch.save()
    del user_list

    # We need to ensure that all courses have `CourseUserGroup`s created. Otherwise we will run into race conditions.
    logger.info('Creating cohorts for Courses - {}'.format(task_log_msg))
    courses = {entry.get('course_id') for entry in clean_user_list}
    for course in courses:
        try:
            add_cohort_for_course(course, 'default_cohort', 'random')
        except ApiError:
            logger.warning('Failed adding cohort for course {} - SKIPPING - {}'.format(course, task_log_msg))
            # We can safely ignore already existing cohorts.
            # We also want to ignore nonexistent courses at this point, because they will be logged later.
            pass

    logger.info('Attempting to register {} Users - {}'.format(len(clean_user_list), task_log_msg))

    # The bottleneck with processing these users from the POV of Apros is the network, i.e. when we wait for the
    # LMS to process the user and return an HTTP response. Thus we run this in multiple threads with batches.
    total_clean_users = len(clean_user_list)
    pool_size = settings.MAX_IMPORT_JOB_THREAD_POOL_SIZE or 4
    batch_size = total_clean_users // pool_size or 1
    pool = ThreadPool(pool_size)
    threads = []
    for index in xrange(0, total_clean_users, batch_size):
        batch = clean_user_list[index:min(index + batch_size, total_clean_users)]
        threads.append(
            pool.apply_async(
                enroll_participants,
                args=(
                    batch,
                    is_internal_admin,
                    registration_batch,
                    register,
                )
            )
        )

    # Run queued up jobs.
    for thread in threads:
        thread.get()

    logger.info('{} of {} users registered successfully - {}'
                .format(registration_batch.succeded, total_clean_users, task_log_msg))
    logger.info('Completed - {}'.format(task_log_msg))

    generate_import_files_and_send_notification.delay(
        batch_id=registration_batch.task_key,
        user_id=user_id,
        base_url=base_url,
        user_file_name=registration_batch.uploaded_file_name,
        import_type='register' if register else 'enroll',
    )

    try:
        storage.delete(file_path)
    except Exception as e:
        logger.error('{} - Exception while deleting file: {}'.format(task_log_msg, e.message))
    else:
        logger.info('{} - Successfully deleted CSV file: {}'.format(task_log_msg, file_path))


@task(name='admin.delete_company_task', queue='high_priority')
def delete_company_task(company_id, owner, base_url):
    """
    Deletes company by:
    1. invoking `delete_participants_task` as function, because we don't want to proceed in case of any error,
    2. invoking `delete_company_data` for removing other company data.
    """
    started = time.time()
    company_name = 'Unknown'
    try:
        # Fetch organization
        organization = organization_api.fetch_organization(company_id)
        company_name = organization.display_name
        # Delete users in organization
        user_ids = organization_api.fetch_organization_user_ids(company_id)
        delete_participants_task(
            user_ids,
            send_confirmation_email=True,
            owner=owner,
            base_url=base_url,
            email_template='admin/delete_company_email_template.haml',
            email_subject=_('Company deletion completed'),
            template_extra_data={'company_name': company_name}
        )
        # Delete organization profile
        delete_company_data(company_id)
    except Exception as e:
        subject = _('Company deletion completed')
        email_template = 'admin/delete_company_profile_email_template.haml'
        template_data = {
            'company_name': company_name,
            'first_name': owner.get('first_name', 'admin').capitalize(),
            'mcka_logo_url': urljoin(
                base=base_url,
                url='/static/image/mcka_email_logo.png'
            ),
            'minutes_taken': math.ceil((time.time() - started) / 60),
            'reason': str(e),
        }
        task_log_msg = "Delete Company profile task"
        send_email.delay(subject, email_template, template_data, [owner.get('email')], task_log_msg)


@task(name='admin.delete_participants_task', queue='high_priority')
def delete_participants_task(
        users_to_delete,
        send_confirmation_email,
        owner,
        base_url,
        email_template='admin/delete_users_email_template.haml',
        email_subject='Bulk deletion completed',
        template_extra_data=None
):
    """
    Extract users from CSV, delete them and (optionally) send an email to the `owner` - user that initiated deletion.
    :param users_to_delete: you need to provide either:
        - `str` being an URL to a CSV file containing users who should be deleted,
        - `list` or `set` containing users' IDs.
    """
    from admin.controller import delete_participants  # We want to avoid circular imports here.

    task_log_msg = "Delete Participants task"
    file_path = ''
    template_extra_data = template_extra_data or {}

    logger.info('Started - {}'.format(task_log_msg))

    failed, total = {}, 0
    started = time.time()

    if isinstance(users_to_delete, six.string_types):
        # The users for deletion are specified in a CSV file.
        file_path = get_path(users_to_delete)

        try:
            field, emails = get_emails_from_csv(file_path)
            total = len(emails)
            users = []
            for i in range(0, total, settings.DELETION_SYNCHRONOUS_MAX_USERS):
                users += get_users(**{field: emails[i:i + settings.DELETION_SYNCHRONOUS_MAX_USERS]})
        except Exception:
            logger.error('{} - Failed to open file with path: {}'.format(task_log_msg, file_path))
            raise
        else:
            logger.info('Successfully opened CSV file - {}'.format(task_log_msg))

        present_emails = set(user.email for user in users)
        failed.update({email: 'User not found' for email in emails if email not in present_emails})

        failed.update(delete_participants(None, users=users))

        try:
            storage = get_storage(secure=True)
            storage.delete(file_path)
        except Exception as e:
            logger.error('{} - Exception while deleting file: {}'.format(task_log_msg, e.message))
        else:
            logger.info('{} - Successfully deleted CSV file: {}'.format(task_log_msg, file_path))

    elif users_to_delete:
        # We have users' IDs.
        total = len(users_to_delete)
        failed.update(delete_participants(users_to_delete))

    logger.info('Completed - {}'.format(task_log_msg))

    failed_url = None
    if failed:
        fields = OrderedDict([
            ('email', ('email', '')),
            ('reason', ('reason', '')),
        ])
        file_name = 'deletion_errors.csv'
        errors = [{'email': k, 'reason': v} for k, v in failed.items()]
        try:
            failed_url = create_and_store_csv_file(
                fields, errors, DELETE_PARTICIPANTS_DIR,
                file_name, logger, task_log_msg, secure=True
            )
        except Exception as e:
            logger.error('Failed to generate CSV - {} - {}'.format(e.message, task_log_msg))

        failed_url = urljoin(
            base=base_url,
            url=failed_url
        )

    if send_confirmation_email:
        subject = _(email_subject)
        mcka_logo = urljoin(
            base=base_url,
            url='/static/image/mcka_email_logo.png'
        )
        template_data = {
            'first_name': owner.get('first_name'),
            'file_name': file_path.split('/')[-1],
            'mcka_logo_url': mcka_logo,
            'minutes_taken': math.ceil((time.time() - started) / 60),
            'failed_url': failed_url,
            'successful': total - len(failed),
            'total': total,
        }
        template_data.update(template_extra_data)

        send_email.delay(subject, email_template, template_data, [owner.get('email')], task_log_msg)

    if failed:
        raise InvalidTaskError("Failed to delete users.")


@task(name='admin.user_company_fields_update_task', queue='high_priority')
def user_company_fields_update_task(user_id, users_records, base_url):
    task_log_msg = 'Updating company field\'s data for user from csv'
    record_count = 0
    errors = []
    logger.info('Starting - {}'.format(task_log_msg))
    try:
        total_records = len(users_records) - 1
        organization_id = get_organization_by_user_email(users_records[1][0])
        org_fields_csv = users_records[0][1:]
    except (TypeError, IndexError):
        errors.append(_('File is not formatted properly. Please format according to given template.'))
        send_bulk_fields_update_email(user_id, total_records, record_count, errors, base_url)
        return

    csv_keys, errors = validate_company_field(org_fields_csv, organization_id)
    users_records = users_records[1:]
    if errors:
        send_bulk_fields_update_email(user_id, total_records, record_count, errors, base_url)
        return
    else:
        record_count, errors = update_company_field_for_users(users_records, csv_keys, organization_id)
    send_bulk_fields_update_email(user_id, total_records, record_count, errors, base_url)
    logger.info('Successfully finishing - {}'.format(task_log_msg))
    return


@task(name='admin.user_manager_update_task', queue='high_priority')
def bulk_user_manager_update_task(user_id, users_records, base_url):
    task_log_msg = 'Updating manager data for user from csv'
    record_count = 0
    errors = []
    logger.info('Starting - {}'.format(task_log_msg))
    total_records = len(users_records) - 1
    validated_records, errors = validate_participant_and_manager_records(users_records)
    if validated_records:
        for participant, manager in validated_records:
            try:
                create_update_delete_manager(
                    user_id=manager.get('id'),
                    manager_email=manager.get('email'),
                    username=participant.get('username')
                )
                record_count += 1
            except ApiError:
                errors.append(_("User with email {} and manager with email {} was unsuccessfull.")
                              .format(participant.get('email'), manager.get('email')))
    send_bulk_fields_update_email(user_id, total_records, record_count, errors, base_url)


@task(
    name='admin.generate_import_files_and_send_notification',
    max_retries=3
)
def generate_import_files_and_send_notification(batch_id, user_id, base_url, user_file_name, import_type):
    """
    Generates activation links and any error files of batch Import Participants
    process and send notification link
    """
    task_log_msg = "Import Participants notification task for batch {}".format(batch_id)
    logger.info('Generating result files - {}'.format(task_log_msg))

    try:
        registration_batch = UserRegistrationBatch.objects.get(task_key=batch_id)
    except (UserRegistrationBatch.DoesNotExist, UserRegistrationBatch.MultipleObjectsReturned):
        logger.info('Failed retrieving batch - {} - EXITING'.format(task_log_msg))
        return False

    error_records = UserRegistrationError.objects.filter(task_key=registration_batch.task_key)
    activation_links = UserActivation.get_activations_by_task_key(task_key=registration_batch.task_key)

    errors = []
    user_data = {}

    for error in error_records:
        error_data = dict(email=error.user_email, errors=error.error)

        try:
            user_data = json.loads(error.user_data)
        except (TypeError, ValueError):
            user_data = {}

        error_data.update(user_data)
        errors.append(error_data)

    activation_links = [{
        'first_name': activation_link.first_name,
        'last_name': activation_link.last_name,
        'email': activation_link.email,
        'activation_link': create_activation_url(activation_code=activation_link.activation_key, base_url=base_url)}
        for activation_link in activation_links
    ]

    error_file_url = ''
    activations_links_file_url = ''

    if errors:
        if import_type == 'register':
            fields = OrderedDict([
                ("First Name", ("first_name", '')),
                ("Last Name", ("last_name", '')),
                ("Email", ("email", '')),
                ("Company ID", ("company_id", '')),
                ("Course ID", ("course_id", '')),
                ("Status", ("status", '')),
                ("Errors", ("errors", '')),
            ])
        elif import_type == 'enroll':
            fields = OrderedDict([
                ("Email", ("email", '')),
                ("Course ID", ("course_id", '')),
                ("Status", ("status", '')),
                ("Errors", ("errors", '')),
            ])
        else:
            fields = OrderedDict([])

        file_name = '{}_import_errors.csv'.format(registration_batch.task_key)

        try:
            error_file_url = create_and_store_csv_file(
                fields, errors, IMPORT_PARTICIPANTS_DIR,
                file_name, logger, task_log_msg, secure=True
            )
        except Exception as e:
            raise generate_import_files_and_send_notification.retry(exc=e)

    if activation_links:
        fields = OrderedDict([
            ("First Name", ("first_name", '')),
            ("Last Name", ("last_name", '')),
            ("Email", ("email", '')),
            ("Activation Link", ("activation_link", '')),
        ])

        file_name = '{}_activation_links.csv'.format(registration_batch.task_key)

        try:
            activations_links_file_url = create_and_store_csv_file(
                fields, activation_links, IMPORT_PARTICIPANTS_DIR,
                file_name, logger, task_log_msg, secure=True
            )
        except Exception as e:
            raise generate_import_files_and_send_notification.retry(exc=e)

    registration_batch.activation_file_url = activations_links_file_url
    registration_batch.error_file_url = error_file_url
    registration_batch.time_completed = timezone.now()

    try:
        completion_time = (registration_batch.time_completed - registration_batch.time_requested)\
                              .total_seconds() // 60.0
        completion_time = int(completion_time)
    except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
        completion_time = 'N/A'

    registration_batch.save()

    subject = _('Import File Processed')
    email_template = 'admin/import_users_email_template.haml'
    mcka_logo = urljoin(
        base=base_url,
        url='/static/image/mcka_email_logo.png'
    )
    template_data = {
        'file_name': user_file_name,
        'completion_time': completion_time,
        'total': registration_batch.attempted,
        'successful': registration_batch.succeded,
        'error_file_url': urljoin(
            base=base_url,
            url=error_file_url
        ) if error_file_url else '',
        'activation_links_url': urljoin(
            base=base_url,
            url=activations_links_file_url
        ) if activations_links_file_url else '',
        'support_email': settings.MCKA_SUPPORT_EMAIL,
        'mcka_logo_url': mcka_logo,
    }

    try:
        user_data = user_api.get_user(user_id).to_dict()
        template_data.update({'first_name': user_data.get('first_name')})
    except Exception as e:
        logger.error(
            'Failed retrieving Admin User info from API - {} - {}'.format(e.message, task_log_msg)
        )
        raise generate_import_files_and_send_notification.retry(exc=e)
    else:
        try:
            send_email(
                subject=subject,
                email_template=email_template,
                template_data=template_data,
                user_emails=[user_data.get('email')],
                task_log_msg=task_log_msg
            )
        except Exception as e:
            raise generate_import_files_and_send_notification.retry(exc=e)

    return True


@task(name='admin.purge_import_errors_and_csv_files')
def purge_old_import_records_and_csv_files():
    """
    Purges old import/enroll error records and CSV files
    """
    task_log_msg = "Purge Old Import Records Task"

    logger.info('Started - {}'.format(task_log_msg))

    end_date = timezone.now().date() - timedelta(days=14)
    start_date = end_date - timedelta(days=14)

    old_tasks = UserRegistrationBatch.objects.filter(time_requested__range=(start_date, end_date))\
        .values_list('task_key', 'error_file_url', 'activation_file_url')

    old_task_ids = []
    file_paths = []

    for old_task in old_tasks:
        task_id, error_file_url, success_file_url = old_task
        old_task_ids.append(task_id)

        for url in (error_file_url, success_file_url):
            if not url:
                continue

            file_path = get_path(url)

            if file_path:
                file_paths.append(file_path)

    logger.info('Found {} DB records and {} CSV files for deletion - {}'
                .format(len(old_task_ids), len(file_paths), task_log_msg))

    if old_task_ids:
        UserRegistrationError.objects.filter(task_key__in=old_task_ids).delete()
        UserRegistrationBatch.objects.filter(task_key__in=old_task_ids).delete()

        logger.info('Successfully deleted DB records - {}'.format(task_log_msg))

    if file_paths:
        logger.info('Deleting CSV Files - {}'.format(task_log_msg))

        if default_storage == 'storages.backends.s3boto.S3BotoStorage':
            try:
                default_storage.bucket.delete_keys(file_paths)
            except Exception as e:
                logger.error('S3 exception while deleting files {} - {}'.format(e.message, task_log_msg))
            else:
                logger.info('Successfully deleted CSV files - {}'.format(task_log_msg))
        else:
            for path in file_paths:
                try:
                    default_storage.delete(path)
                except OSError:
                    pass

    logger.info('Completed - {}'.format(task_log_msg))

    return True


@task(name='admin.create_tile_progress_data', queue='high_priority')
def create_tile_progress_data(tile_id):
    """
    Creates tile progress data, Triggered when a learner dashboard tile is saved
    """
    try:
        tile = LearnerDashboardTile.objects.get(id=tile_id)
    except LearnerDashboardTile.DoesNotExist:
        logger.info('EXITING Tile Progress Data Creation - Failed retrieving LearnerDashboardTile object with id: {}'
                    .format(tile_id))
        return False
    link = strip_tile_link(tile.link)
    users = json.loads(course_api.get_user_list_json(link['course_id'], page_size=1000))
    completions = course_api.get_course_completions(link['course_id'], page_size=1000)
    for user in users:
        course = get_course_object(user['id'], link['course_id'])
        user_completions = completions.get(user['username'], None)
        if course and user_completions:
            update_progress(tile, user, course, user_completions, link)
    return True


@task(name='admin.create_problem_response_report', bind=True)
def create_problem_response_report(
    self, course_id, problem_locations, problem_types_filter=None
):
    """
    Create a problem response report pertaining to a specific course.
    """
    resp = instructor_api.generate_problem_responses_report(course_id, problem_locations, problem_types_filter)

    self.update_state(task_id=self.request.id, state='PROGRESS', meta={'percentage': 10})
    return {'id': self.request.id, 'remote_task_id': resp['task_id']}


@task(bind=True, name='admin.monitor_problem_response_report', max_retries=30)
def monitor_problem_response_report(self, parent_task, course_id):
    """
    Monitors problem response report task. This task will long-poll for one hour before bailing.
    """
    task = instructor_api.get_task_status(parent_task['remote_task_id'])
    if (task and task['in_progress']):
        raise self.retry(countdown=60 * 2)  # Retry in 2 minutes
    self.update_state(task_id=parent_task['id'], state='PROGRESS', meta={'percentage': 15})
    return {'id': parent_task['id'], 'report_name': task['task_progress']['report_name']}


@task(bind=True, name='admin.post_process_problem_response_report', max_retries=3)
def post_process_problem_response_report(self, parent_task, course_id, problem_locations):
    """
    Post process report to add extra data.
    """
    # If we're running with CELERY_ALWAYS_EAGER the result of the last
    # task is not passed correctly always, because of the self.retry()
    if getattr(settings, 'CELERY_ALWAYS_EAGER', False) and parent_task is None:
        report_task = AdminTask.objects.filter(course_id=course_id, status='PROGRESS').first()
        parent_task = {'id': report_task.task_id, 'report_name': None}
    else:
        report_task = AdminTask.objects.get(task_id=parent_task['id'])
    # Get list of downloads
    downloads = instructor_api.get_report_downloads(course_id, parent_task['report_name'])

    if downloads:
        download = downloads[0]
    else:
        self.update_state(task_id=self.request.id, state='ERROR')
        raise Exception('No Downloads found.')

    self.update_state(task_id=parent_task['id'], state='PROGRESS', meta={'percentage': 20})

    # Initialize processor class.
    processor = ProblemReportPostProcessor(
        course_id=course_id,
        report_name=download['name'],
        report_uri=download['url']
    )

    # Post process rows.
    rows, keys = processor.post_process()
    # We don't know the total number of rows since we're reading the file line by line.
    # And, it's not worth it to read the file twice.
    self.update_state(task_id=parent_task['id'], state='PROGRESS', meta={'percentage': 90})

    # Write csv to a temporary file.
    fields = OrderedDict([(key, (key, '')) for key in keys])
    # Create remote path to report.
    csv_name = u"{course_prefix}_{timestamp}.csv".format(
        course_prefix=course_id.replace('/', '_'),
        timestamp=report_task.requested_datetime.strftime("%Y-%m-%d-%H%M")
    )
    # Store file
    hashed_course_id = hashlib.sha1(course_id).hexdigest()
    dir_name = os.path.join('reports', hashed_course_id)
    task_log_msg = 'post processing problem response report'
    file_path = create_and_store_csv_file(fields, rows, dir_name, csv_name, logger, task_log_msg)

    if file_path.startswith('http'):
        file_url = file_path
    else:
        file_url = reverse('private_storage', kwargs={'path': file_path})
    self.update_state(task_id=parent_task['id'], state='PROGRESS', meta={'percentage': 100})

    # Update Database
    report_task.output = json.dumps({'url': file_url, 'name': csv_name})
    report_task.status = 'DONE'
    report_task.save()
    return {'file_url': file_url, 'username': report_task.username}


@task(name='admin.send_problem_response_report_success_email', max_retries=3)
def send_problem_response_report_success_email(parent_task):
    user_detail = user_api.get_users(username=parent_task['username'])
    send_html_email(
        subject=_('Problem Response Report'),
        to_emails=[user_detail[0].email],
        template_name='admin/problem_response_report_email.haml',
        template_data={'success': True,
                       'first_name': user_detail[0].first_name,
                       'file_url': parent_task['file_url']}
    )


@task(bind=True)
def handle_admin_task_error(self, error_task_id, res_id):
    """
    Handle Admin Task error.

    Args:
        error_task_uuid (str): Uuid of the task that raised the error.
    """
    async_res = self.AsyncResult(task_id=error_task_id)
    admin_task = AdminTask.objects.get(task_id=res_id)
    admin_task.status = 'ERROR'
    admin_task.output = async_res.result
    admin_task.save()
    user_detail = user_api.get_users(username=admin_task.username)
    send_html_email(
        subject=_('Problem Response Report'),
        to_emails=[user_detail[0].email],
        template_name='admin/problem_response_report_email.haml',
        template_data={
            'success': False,
            'first_name': user_detail[0].first_name,
        },
    )
    logger.error('Admin Task failed with the following output: {}'.format(admin_task.output))
