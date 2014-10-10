''' Objects for users / authentication built from json responses from API '''
import json
import os
from datetime import datetime
from .json_object import JsonObject, JsonObjectWithImage
import organization_api
from django.conf import settings
from django.core.files.storage import default_storage


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
        ''' return default avatar unless the user has one '''
        # TODO: is the size param going to be used here?

        try:
            if hasattr(self, 'logo_url') and self.logo_url is not None:
                usable_sizes = [s for s in settings.GENERATE_IMAGE_SIZES if s >= size]
                best_image_size = min(usable_sizes) if len(usable_sizes) > 0 else None

                # if we are asking for one of the specific sizes but it does not exist, then clean any old ones and regenerate
                if best_image_size and size == best_image_size and not self.have_size(size):
                    self._clean_and_resize_images()

                image_url = self.logo_url

                if best_image_size and self.have_size(best_image_size):
                    image_url = self._get_specific_size_url(best_image_size)

                if not default_storage.exists(self._strip_proxy_image_url(image_url)):
                    image_url = JsonObjectWithImage.default_image_url()
                elif path == 'absolute' and settings.DEFAULT_FILE_STORAGE != 'django.core.files.storage.FileSystemStorage':
                    image_url = default_storage.url(
                        self._strip_proxy_image_url(image_url)
                    )
            else:
                image_url = JsonObjectWithImage.default_image_url()
        except:
            image_url = JsonObjectWithImage.default_image_url()

        return image_url

    def _get_specific_size_url(self, size):
        return "{}-{}.jpg".format(os.path.splitext(self.logo_url)[0], size)

    def _clean_and_resize_images(self):
        for delete_size in settings.REMOVE_IMAGE_SIZES:
            if self.have_size(delete_size):
                self.delete_size(delete_size)

        image_path = self._strip_proxy_image_url(self.logo_url)
        if default_storage.exists(image_path):
            from PIL import Image
            original_image = Image.open(
                default_storage.open(image_path)
            )
            self.save_profile_image(original_image, image_path)


class OrganizationList(JsonObject):
    object_map = {
        "results": Organization
    }
