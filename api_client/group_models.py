''' Objects for users / authentication built from json responses from API '''
import json
from datetime import datetime
from .json_object import JsonObject
import group_api


class GroupInfo(JsonObject):

    ''' object representing a group from api json response '''
    #required_fields = ["name", "id"]
    data_fields = []
    group_type = None

    def __init__(self, json_data=None, dictionary=None):
        if json_data and dictionary is None:
            dictionary = json.loads(json_data)

        # has additional attributes in embedded data
        if "data" in dictionary:
            for data_attr in self.data_fields:
                if data_attr in dictionary["data"]:
                    dictionary[data_attr] = dictionary["data"][data_attr]

        super(GroupInfo, self).__init__(
            json_data=None,
            dictionary=dictionary
        )

    def get_users(self):
        return group_api.get_users_in_group(self.id)

    def get_groups(self, *args, **kwargs):
        return group_api.get_groups_in_group(self.id, *args, **kwargs)

    @classmethod
    def _clean_group_data(cls, group_data):
        clean_data = {
            key: value for key, value in group_data.iteritems() if key in cls.data_fields
        }

        for date_field in cls.date_fields:
            date_components = ["{}_{}".format(date_field, component_value)
                               for component_value in ['year', 'month', 'day']]
            component_values = [int(group_data[component])
                                for component in date_components if component in group_data]
            if len(component_values) == 3:
                clean_data[date_field]= datetime(
                    component_values[0],
                    component_values[1],
                    component_values[2]
                ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        return clean_data

    @classmethod
    def create(cls, name, group_data):
        return group_api.create_group(name, cls.group_type, group_data=cls._clean_group_data(group_data), group_object=cls)

    @classmethod
    def list(cls):
        return group_api.get_groups_of_type(cls.group_type, group_object=cls)

    @classmethod
    def fetch(cls, group_id):
        return group_api.fetch_group(group_id, group_object=cls)

    @classmethod
    def delete(cls, group_id):
        return group_api.delete_group(group_id)

    @classmethod
    def update(cls, group_id, group_data):
        return group_api.update_group(group_id, cls.group_type, cls._clean_group_data(group_data), group_object=cls)
