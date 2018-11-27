from django.conf import settings


from api_client.mobileapp_api import get_mobile_apps
from api_client.api_error import ApiError
from admin.models import (
    ClientCustomization, ClientNavLinks, BrandingSettings
)

from .common import DataManager
from lib.utils import DottableDict


ORGANIZATION_PROPERTIES = DottableDict(
    BRANDING='branding',
    MOBILE_APPS='mobile_apps',
)


class OrgDataManager(DataManager):
    cache_key_prefix = 'org'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('org_data')

    def __init__(self, org_id):
        self.organization_id = org_id
        self.cache_unique_identifier = self.organization_id

    def get_branding_data(self):
        branding_data = self.get_cached_data(property_name=ORGANIZATION_PROPERTIES.BRANDING)

        if branding_data is not None:
            return branding_data

        try:
            client_customization = ClientCustomization.objects.get(client_id=self.organization_id)
        except ClientCustomization.DoesNotExist:
            client_customization = None

        try:
            branding = BrandingSettings.objects.get(client_id=self.organization_id)
        except BrandingSettings.DoesNotExist:
            branding = None

        client_nav_links = ClientNavLinks.objects.filter(client_id=self.organization_id)
        client_nav_links = dict((link.link_name, link) for link in client_nav_links)

        org_branding_data = DottableDict(
            customization=client_customization,
            branding=branding,
            nav_links=client_nav_links
        )

        self.set_cached_data(
            property_name=ORGANIZATION_PROPERTIES.BRANDING,
            data=org_branding_data
        )

        return org_branding_data

    def get_org_common_data(self):
        """
        Utility method for getting cache based organization data

        stores:
            branding
            customization
            navigation links
            mobile apps
        """
        branding_data = self.get_branding_data()
        mobile_apps = self.get_cached_data(property_name=ORGANIZATION_PROPERTIES.MOBILE_APPS)

        if mobile_apps is None:
            try:
                mobile_apps = get_mobile_apps({"organization_ids": self.organization_id})
            except ApiError:
                mobile_apps = {}
            else:
                self.set_cached_data(
                    property_name=ORGANIZATION_PROPERTIES.MOBILE_APPS,
                    data=mobile_apps
                )

        return DottableDict(
            mobile_apps=mobile_apps,
            customization=branding_data.customization,
            branding=branding_data.branding,
            nav_links=branding_data.nav_links
        )
