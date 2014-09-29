''' Objects for users / authentication built from json responses from API '''
import json
from datetime import datetime
from .json_object import JsonObject, JsonObjectWithImage
import organization_api
from django.conf import settings


class Organization(JsonObjectWithImage):
    #required_fields = ["display_name", "contact_name", "contact_phone", "contact_email", ]

    ''' object representing a organization from api json response '''
    @classmethod
    def create(cls, name, organization_data):
        return organization_api.create_organization(name, organization_data=organization_data, organization_object=cls)

    @classmethod
    def fetch(cls, organization_id):
        return organization_api.fetch_organization(organization_id, organization_object=cls)

    @classmethod
    def list(cls):
        return organization_api.get_organizations(organization_object=cls)

    @classmethod
    def delete(cls, organization_id):
        return organization_api.delete_organization(organization_id)

    @classmethod
    def update_and_fetch(cls, organization_id, update_hash):
        return organization_api.update_organization(organization_id, update_hash, organization_object=cls)

    @classmethod
    def fetch_from_url(cls, url):
        return organization_api.fetch_organization_from_url(url, organization_object=cls)

    def add_user(self, user_id):
        if user_id not in self.users:
            self.users.append(user_id)
            organization_api.update_organization(self.id, {"users": self.users})

    def remove_user(self, user_id):
        if user_id in self.users:
            self.users.remove(user_id)
            organization_api.update_organization(self.id, {"users": self.users})

    def add_group(self, group_id):
        if group_id not in self.groups:
            self.groups.append(group_id)
            organization_api.update_organization(self.id, {"groups": self.groups})

    def remove_group(self, group_id):
        if group_id in self.groups:
            self.groups.remove(user_id)
            organization_api.update_organization(self.id, {"groups": self.groups})

    def image_url(self, size=48, path='absolute'):
        ''' return default logo unless the user has one '''
        # TODO: is the size param going to be used here?
        if hasattr(self, 'logo_url') and self.logo_url is not None:
            if size <= 48:
                image_url = self.logo_url[:-4] + '-48.jpg'
            elif size <= 160:
                image_url = self.logo_url[:-4] + '-160.jpg'
            else:
                image_url = self.logo_url

            if path == 'absolute' and settings.DEFAULT_FILE_STORAGE != 'django.core.files.storage.FileSystemStorage':
                from django.core.files.storage import default_storage
                image_url = default_storage.url(
                    self._strip_proxy_image_url(image_url))
        else:
            image_url = self.default_image_url()
        return image_url


class OrganizationList(JsonObject):
    object_map = {
        "results": Organization
    }
