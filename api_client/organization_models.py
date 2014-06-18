''' Objects for users / authentication built from json responses from API '''
import json
from datetime import datetime
from .json_object import JsonObject
import organization_api


class OrganizationInfo(JsonObject):

    ''' object representing a organization from api json response '''
    data_fields = []

    def __init__(self, json_data=None, dictionary=None):
        if json_data and dictionary is None:
            dictionary = json.loads(json_data)

        # has additional attributes in embedded data
        if "data" in dictionary:
            for data_attr in self.data_fields:
                if data_attr in dictionary["data"]:
                    dictionary[data_attr] = dictionary["data"][data_attr]

        super(OrganizationInfo, self).__init__(
            json_data=None,
            dictionary=dictionary
        )

    def get_users(self):
        return organization_api.get_users_in_organization(self.id)

    def get_organizations(self, params=None):
        if params:
            return organization_api.get_groups_in_organization(self.id, params=params)
        else:
            return organization_api.get_groups_in_organization(self.id)

    @classmethod
    def _clean_organization_data(cls, organization_data):
        clean_data = {
            key: value for key, value in organization_data.iteritems() if key in cls.data_fields
        }

        for date_field in cls.date_fields:
            date_components = ["{}_{}".format(date_field, component_value)
                               for component_value in ['year', 'month', 'day']]
            component_values = [int(organization_data[component])
                                for component in date_components if component in organization_data]
            if len(component_values) == 3:
                clean_data[date_field]= datetime(
                    component_values[0],
                    component_values[1],
                    component_values[2]
                ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        return clean_data

    @classmethod
    def create(cls, name, organization_data):
        return organization_api.create_organization(name, organization_data=cls._clean_organization_data(organization_data), organization_object=cls)

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
    def update(cls, organization_id, organization_data):
        return organization_api.update_organization(organization_id, cls._clean_organization_data(organization_data), organization_object=cls)
