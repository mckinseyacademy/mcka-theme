from django.utils import timezone
from .models import LicenseGrant
from django.utils.translation import ugettext as _


class NoAvailableLicensesError(Exception):
    '''
    Exception to be thrown when no licenses are available for use
    '''

    def __str__(self):
        return _("No Available licenses")


def create_licenses(granted_id, grantor_id, license_count):
    for i in range(0, license_count):
        license = LicenseGrant(granted_id=granted_id, grantor_id=grantor_id)
        license.save()


def licenses_report(granted_id, grantor_id):
    licenses = LicenseGrant.objects.filter(
        granted_id=granted_id,
        grantor_id=grantor_id
    )
    allocated = len(licenses)
    assigned = len(
        [license for license in licenses if license.grantee_id is not None])

    return allocated, assigned


def assigned_licenses(granted_id, grantor_id):
    licenses = LicenseGrant.objects.filter(
        granted_id=granted_id,
        grantor_id=grantor_id
    )
    return [license for license in licenses if license.grantee_id is not None]


def assign_license(granted_id, grantor_id, grantee_id):
    # perhaps already assigned?
    already_granted = LicenseGrant.objects.filter(
        granted_id=granted_id,
        grantor_id=grantor_id,
        grantee_id=grantee_id
    )

    if len(already_granted) > 0:
        return already_granted[0]

    licenses = LicenseGrant.objects.filter(
        granted_id=granted_id,
        grantor_id=grantor_id,
        grantee_id=None
    )
    if len(licenses) < 1:
        raise NoAvailableLicensesError()

    license = licenses[0]
    license.grantee_id = grantee_id
    license.granted_on = timezone.now()

    license.save()

    return license


def revoke_license(granted_id, grantor_id, grantee_id):
    licenses = LicenseGrant.objects.filter(
        granted_id=granted_id,
        grantor_id=grantor_id,
        grantee_id=grantee_id
    )
    if len(licenses) < 1:
        raise NoAvailableLicensesError()

    license = licenses[0]
    license.grantee_id = None
    license.granted_on = None

    license.save()


def fetch_granted_license(granted_id, grantee_id):
    licenses = LicenseGrant.objects.filter(granted_id=granted_id, grantee_id=grantee_id)
    if len(licenses) < 1:
        return None
    else:
        return licenses[0]


def fetch_granted_licenses(grantee_id, grantor_id):
    licenses = LicenseGrant.objects.filter(grantee_id=grantee_id, grantor_id=grantor_id)
    if len(licenses) < 1:
        return None
    else:
        return licenses


class LicenseBroker(object):

    """
    Useful class based for repeated operations for licenses. Perhaps not particularly useful because mostly not a
    problem, but easy and perhaps handy
    """
    granted_id = None
    grantor_id = None

    def __init__(self, granted_id, grantor_id):
        self.granted_id = granted_id
        self.grantor_id = grantor_id

    def create(self, license_count):
        create_licenses(self.granted_id, self.grantor_id, license_count)

    def report(self):
        licenses_report(self.granted_id, self.grantor_id)

    def assign(self, grantee_id):
        assign_license(self.granted_id, self.grantor_id, grantee_id)

    def revoke(self, grantee_id):
        revoke_license(self.granted_id, self.grantor_id, grantee_id)

    def assigned(self):
        return assigned_licenses(self.granted_id, self.grantor_id)
