''' Objects for users / authentication built from json responses from API '''
import json
from datetime import datetime, date

from django.utils.translation import ugettext as _

from .json_object import JsonObject
import group_api


class GroupInfo(JsonObject):

    ''' object representing a group from api json response '''
    # required_fields = ["name", "id"]
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
                else:
                    dictionary[data_attr] = None

        super(GroupInfo, self).__init__(
            json_data=None,
            dictionary=dictionary
        )

    def get_users(self):
        return group_api.get_users_in_group(self.id)

    def get_groups(self, *args, **kwargs):
        return group_api.get_groups_in_group(self.id, *args, **kwargs)

    def get_workgroups(self):
        return group_api.get_workgroups_in_group(self.id)

    def add_course(self, course_id):
        return group_api.add_course_to_group(course_id, self.id)

    @classmethod
    def _clean_group_data(cls, group_data):
        clean_data = {
            key: value for key, value in group_data.iteritems() if key in cls.data_fields
        }

        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        for date_field in cls.date_fields:
            if date_field in clean_data and type(clean_data[date_field]) in (date, datetime):
                clean_data[date_field] = clean_data[date_field].strftime(date_format)
            else:
                date_components = [_("{date_field}_{component_value}").format(
                    date_field=date_field,
                    component_value=component_value)
                                   for component_value in ['year', 'month', 'day']]
                component_values = [int(group_data[component])
                                    for component in date_components if component in group_data]
                if len(component_values) == 3:
                    clean_data[date_field]= datetime(
                        component_values[0],
                        component_values[1],
                        component_values[2]
                    ).strftime(date_format)

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
    def update(cls, group_id, name, group_data):
        return group_api.update_group(group_id, name, cls.group_type, cls._clean_group_data(group_data), group_object=cls)
