import re
import logging

from urllib.parse import urlparse, urljoin
import requests

from django.core.management.base import BaseCommand
from django.db.models import Q

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


class Command(BaseCommand):
    help = 'Updates the assets links to point to correct server and course'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            help='domain of environment we are running on e.g; qa.mckinsey.edx.org',
        )

    def handle(self, *args, **options):
        environment = options.get('environment')

        ld_items = LearnerDashboardDiscovery.objects.filter(link__contains='/c4x/')
        content_items = CuratedContentItem.objects.filter(
            Q(url__contains='/c4x/') |
            Q(thumbnail_url__contains='/c4x/') |
            Q(image_url__contains='/c4x/')
        )

        logger.info('Updating CuratedContentItem table. Found {} records'.format(content_items.count()))

        for item in content_items:
            update_item = False
            for col in ('url', 'thumbnail_url', 'image_url'):
                update, link = check_and_update_asset(getattr(item, col), item.course_id, environment)
                if update:
                    setattr(item, col, link)
                    update_item = True

            if update_item:
                item.save()

        logger.info('Updating LearnerDashboardDiscovery table. Found {} records'.format(ld_items.count()))

        for item in ld_items:
            update, link = check_and_update_asset(item.link, item.learner_dashboard.course_id, environment)
            if update:
                item.link = link
                item.save()


def check_and_update_asset(url, course_id, environment):
    update_record = False
    correct_url = None

    parsed_url = urlparse(url)
    asset_url = ASSET_URL_RE.match(parsed_url.path)

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
                correct_url = create_asset_link(environment, org, course, asset_url.groupdict().get('name'))
                if lms_asset_exists(correct_url):
                    update_record = True
                    logger.info(' Successfully replaced "{}" with "{}" in course "{}"'
                                .format(url, correct_url, course_id))
                else:
                    logger.info('Identical asset does not exists. '
                                'Could not update url "{}" in course "{}"'.format(url, course_id))

    return update_record, correct_url


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
