"""
Celery tasks related to admin app
"""
import json
from collections import OrderedDict
from multiprocessing.pool import ThreadPool
from tempfile import TemporaryFile
from datetime import timedelta
from urlparse import urljoin

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _
from django.conf import settings
from django.urls import reverse, resolve, Resolver404
from django.utils import timezone

from celery.decorators import task
from celery.utils.log import get_task_logger
from celery import states as celery_states
from celery.exceptions import Ignore, MaxRetriesExceededError, Reject

from accounts.helpers import get_organization_by_user_email
from api_client import course_api
from api_client import group_api
from api_client import user_api
from api_client.api_error import ApiError
from util.csv_helpers import CSVWriter, create_and_store_csv_file
from util.s3_helpers import PrivateMediaStorageThroughApros, get_storage
from util.email_helpers import send_html_email

from accounts.models import UserActivation
from accounts.helpers import create_activation_url

from .controller import (
    _enroll_participants,
    _process_line_register_participants_csv,
    build_student_list_from_file,
    create_update_delete_manager,
    validate_participant_and_manager_records,
    validate_company_field,
    update_company_field_for_users,
    CourseParticipantStats,
)
from .models import UserRegistrationError, UserRegistrationBatch

logger = get_task_logger(__name__)
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
        'per_page': 1000,
        'page_size': 1000,
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

        for field in participant.get('attributes'):
            attributes[field['key']] = field['label']
            participant[field['key']] = field['value']

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
    total = len(user_ids)
    added = 0
    failed = 0
    batch_size = 100

    for i in xrange(0, total, batch_size):
        user_ids_batch = user_ids[i:i+batch_size]
        try:
            group_api.add_users_to_group(user_ids_batch, program_id)
            added += len(user_ids_batch)
        except ApiError:
            failed += len(user_ids_batch)
        finally:
            percentage = (100.0 / (total or 1)) * (added + failed)

            # ToDo: Look into updating progress in batches to
            # reduce DB hits for state updates
            users_program_association_task.update_state(
                task_id=task_id, state='PROGRESS', meta={'percentage': int(percentage)}
            )

    return {'successful': added, 'total': total}


@task(name='admin.import_participants_task', queue='high_priority')
def import_participants_task(user_id, base_url, file_url, is_internal_admin, registration_batch_id):
    """
    Processes a CSV file of participants.
    """
    task_log_msg = "Import Participants task"

    logger.info('Started - {}'.format(task_log_msg))

    storage = get_storage(secure=True)
    try:
        file_stream = storage.open(file_url)
    except Exception as e:
        logger.error('{} - Failed to open file with url: {}'.format(task_log_msg, file_url))
        raise

    user_list = build_student_list_from_file(file_stream, parse_method=_process_line_register_participants_csv)
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
        threads.append(pool.apply_async(
            _enroll_participants, args=(batch,
                                        is_internal_admin,
                                        registration_batch,
                                        )
        ))

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
        user_file_name=file_stream.name,
    )

    try:
        storage.delete(file_url)
    except Exception as e:
        logger.error('{} - Exception while deleting file: {}'.format(task_log_msg, e.message))
    else:
        logger.info('{} - Successfully deleted CSV file: {}'.format(task_log_msg, file_url))


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
def generate_import_files_and_send_notification(batch_id, user_id, base_url, user_file_name):
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
        fields = OrderedDict([
            ("First Name", ("first_name", '')),
            ("Last Name", ("last_name", '')),
            ("Email", ("email", '')),
            ("Company ID", ("company_id", '')),
            ("Course ID", ("course_id", '')),
            ("Status", ("status", '')),
            ("Errors", ("errors", '')),
        ])

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

    logger.info('Sending notification email - {}'.format(task_log_msg))

    try:
        user_data = user_api.get_user(user_id).to_dict()
    except Exception as e:
        logger.error(
            'Failed retrieving Admin User info from API - {} - {}'.format(e.message, task_log_msg)
        )
        raise generate_import_files_and_send_notification.retry(exc=e)
    else:
        try:
            send_html_email(
                subject=subject,
                to_emails=[user_data.get('email')], template_name=email_template,
                template_data={
                    'first_name': user_data.get('first_name'),
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
            )
        except Exception as e:
            logger.error('Failed sending notification email to Admin {} - {}'.format(e.message, task_log_msg))
            raise generate_import_files_and_send_notification.retry(exc=e)

    logger.info('Email successfully sent - {}'.format(task_log_msg))

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

            try:
                file_path = resolve(url).kwargs.get('path')
            except Resolver404:
                file_path = url

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
