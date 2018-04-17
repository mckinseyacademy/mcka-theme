from django.conf import settings
from django.core.urlresolvers import reverse

from storages.backends.s3boto import S3BotoStorage

from lib.authorization import is_user_in_permission_group
from api_client.group_api import PERMISSION_GROUPS


EXPORT_STATS_ALLOWED_GROUPS = [
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN, PERMISSION_GROUPS.COMPANY_ADMIN
]


class PrivateMediaStorage(S3BotoStorage):
    """
    S3 storage class to use for private files. URLs with expiry times
    are generated to access files
    """
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    querystring_auth = True
    gzip = True

    bucket_name = getattr(settings, 'AWS_SECURE_STORAGE_BUCKET_NAME', 'AWS_STORAGE_BUCKET_NAME')
    querystring_expire = getattr(settings, 'AWS_SECURE_STORAGE_EXPIRY', 'AWS_QUERYSTRING_EXPIRE')
    access_key = getattr(settings, 'AWS_SECURE_STORAGE_ACCESS_KEY_ID', 'AWS_S3_ACCESS_KEY_ID')
    secret_key = getattr(settings, 'AWS_SECURE_STORAGE_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')

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

    def can_access(self, file_name, user):
        """
        Checks if request user can access this resource
        """
        allowed_groups = self._get_permission_groups(file_name)

        if allowed_groups:
            return is_user_in_permission_group(user, *allowed_groups)
        else:
            return True
