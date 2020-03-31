import re
import logging
import csv
from io import StringIO

from urllib.parse import urlparse, urljoin
import requests

from django.db.models import Q
from django.core.mail import EmailMessage
from django.conf import settings

from celery.decorators import task

from main.models import CuratedContentItem
from admin.models import LearnerDashboardDiscovery

logger = logging.getLogger(__name__)

ASSET_URL_RE = re.compile(r"""
    /?c4x/
    (?P<org>[^/]+)/
    (?P<course>[^/]+)/
    (?P<category>[^/]+)/
    (?P<name>[^/]+)
""", re.VERBOSE | re.IGNORECASE)


def send_report(rows, update_script, email_ids):
    if update_script:
        headers = ['Asset', 'Course', 'Module', 'Updated']
    else:
        headers = ['Asset', 'Course', 'Module', 'Available']

    assets_report = StringIO()
    writer = csv.writer(assets_report)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    subject = '{} Apros assets with incorrect urls task completed'.format('Update' if update_script else 'Get')
    email = EmailMessage(subject, '', settings.APROS_EMAIL_SENDER, email_ids)
    email.attach('apros_assets_report.csv', assets_report.getvalue(), 'text/csv')
    email.send(fail_silently=False)


@task(name='assets.update_lms_asset_links')
def update_lms_asset_links(environment, course_ids, email_ids, update=False):
    """
    Task to update LMS course asset links used in Apros
    """
    report_rows = []
    ld_items = LearnerDashboardDiscovery.objects.filter(link__contains='/c4x/')
    content_items = CuratedContentItem.objects.filter(
        Q(url__contains='/c4x/') |
        Q(thumbnail_url__contains='/c4x/') |
        Q(image_url__contains='/c4x/')
    )

    if course_ids:
        ld_items = ld_items.filter(learner_dashboard__course_id__in=course_ids)
        content_items = content_items.filter(course_id__in=course_ids)

    logger.info('CuratedContentItem table. Found {} records'.format(content_items.count()))

    for item in content_items:
        update_item = False
        for col in ('url', 'thumbnail_url', 'image_url'):
            asset, course, asset_available, correct_url = check_and_update_asset(
                getattr(item, col), item.course_id,
                environment
            )

            if asset:
                if asset_available:
                    setattr(item, col, correct_url)
                    update_item = True

                report_rows.append([asset, course, 'CuratedContent', asset_available])

        if update_item and update:
            item.save()

    logger.info('LearnerDashboardDiscovery table. Found {} records'.format(ld_items.count()))

    for item in ld_items:
        asset, course, asset_available, correct_url = check_and_update_asset(
            item.link, item.learner_dashboard.course_id,
            environment
        )

        if asset:
            if asset_available and update:
                item.link = correct_url
                item.save()

            report_rows.append([asset, course, 'LearnerDashboardDiscovery', asset_available])

    send_report(report_rows, update, email_ids)


def check_and_update_asset(url, course_id, environment):
    asset = None
    asset_available = False
    correct_url = None

    parsed_url = urlparse(url)
    asset_url = ASSET_URL_RE.match(str(parsed_url.path))

    if asset_url is not None:
        try:
            course = course_id.split('/')[1]
            org = course_id.split('/')[0]
        except IndexError:
            pass
        else:
            # check if asset URL belongs to some other server or course
            if parsed_url.hostname != environment or asset_url.groupdict().get('course') != course:
                # check if asset exists at updated url
                asset = asset_url.groupdict().get('name')
                correct_url = create_asset_link(environment, org, course, asset)
                if lms_asset_exists(correct_url):
                    asset_available = True
                    logger.info(' Successfully replaced "{}" with "{}" in course "{}"'
                                .format(url, correct_url, course_id))
                else:
                    logger.info('Identical asset does not exists. '
                                'Could not update url "{}" in course "{}"'.format(url, course_id))

    return asset, course_id, asset_available, correct_url


def create_asset_link(domain, org, course, asset_name):
    asset_path = '/c4x/{}/{}/asset/{}'.format(org, course, asset_name)
    return urljoin('https://{}'.format(domain), asset_path)


def lms_asset_exists(asset_link):
    """
    Checks if asset exists by hitting the url and checking
    if a response is returned
    """
    try:
        request = requests.get(asset_link)
    except Exception:  # pylint: disable=bare-except
        return False
    else:
        return request.status_code == 200
