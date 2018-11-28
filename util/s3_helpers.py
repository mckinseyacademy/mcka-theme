from urlparse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse

from storages.backends.s3boto import S3BotoStorage

from lib.authorization import is_user_in_permission_group
from admin.helpers.permissions_helpers import export_stats_permission_check
from api_client.group_api import PERMISSION_GROUPS


EXPORT_STATS_ALLOWED_GROUPS = [
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN, PERMISSION_GROUPS.COMPANY_ADMIN
]


def exports_stats_check(user, path):
    """
    Implements exports stats permissions based on path
    """
    company_id = None
    course_id = None

    _, resource_path = path.split(settings.EXPORT_STATS_DIR + '/')
    path_parts = resource_path.split('/')
    if len(path_parts) == 3:
        company_id, course_id, _ = path_parts
    elif len(path_parts) == 2:
        course_id, _ = path_parts

    if course_id:
        course_id = course_id.replace('__', '/')

    return export_stats_permission_check(user, company_id, course_id)


class PrivateMediaStorage(S3BotoStorage):
    """
    S3 storage class to use for private files. URLs with expiry times
    are generated to access files and files are saved with S3 provided
    encryption
    """
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    querystring_auth = True
    gzip = True
    encryption = True

    def __init__(self, url_expiry_time=None):
        super(PrivateMediaStorage, self).__init__(
            querystring_expire=url_expiry_time or self.querystring_expire
        )


class PrivateMediaStorageThroughApros(PrivateMediaStorage):
    """
    S3 storage class to use for private files.
    Apros endpoint is used to access files
    """
    def url(self, name, base_url=None, headers=None, response_headers=None, expire=None):
        """
        Creates an Apros url for accessing resource instead of S3's url
        """
        if base_url:
            return urljoin(
                base=base_url,
                url=reverse('private_storage', kwargs={'path': name})
            )
        else:
            return reverse('private_storage', kwargs={'path': name})

    def _get_permission_groups(self, path):
        """
        Gets permissions groups for resource
        determined from resource path
        """
        if settings.EXPORT_STATS_DIR in path:
            return EXPORT_STATS_ALLOWED_GROUPS
        else:
            return []

    def _additional_permission_checks(self, user, path):
        """
        Additional permissions checks to apply for resource
        """
        if settings.EXPORT_STATS_DIR in path:
            return exports_stats_check(user, path)
        else:
            return True

    def can_access(self, file_name, user):
        """
        Checks if request user can access this resource
        """
        allowed_groups = self._get_permission_groups(file_name)

        groups_check = is_user_in_permission_group(user, *allowed_groups) if allowed_groups else True
        additional_checks = self._additional_permission_checks(user, file_name)

        return groups_check and additional_checks
