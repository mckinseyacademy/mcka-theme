''' Objects for users / authentication built from json responses from API '''
import json
from datetime import datetime
from .json_object import JsonObject
import workgroup_api


class WorkGroupInfo(JsonObject):

    ''' object representing a workgroup from api json response '''
    #required_fields = ["name", "id"]
    data_fields = []
    workgroup_type = None

    def __init__(self, json_data=None, dictionary=None):
        if json_data and dictionary is None:
            dictionary = json.loads(json_data)

        # has additional attributes in embedded data
        if "data" in dictionary:
            for data_attr in self.data_fields:
                if data_attr in dictionary["data"]:
                    dictionary[data_attr] = dictionary["data"][data_attr]

        super(WorkGroupInfo, self).__init__(
            json_data=None,
            dictionary=dictionary
        )

    def get_users(self):
        return workgroup_api.get_users_in_group(self.id)

    def get_workgroups(self, params=None):
        if params:
            return workgroup_api.get_groups_in_group(self.id, params=params)
        else:
            return workgroup_api.get_groups_in_group(self.id)

    @classmethod
    def _clean_workgroup_data(cls, workgroup_data):
        clean_data = {
            key: value for key, value in workgroup_data.iteritems() if key in cls.data_fields
        }

        for date_field in cls.date_fields:
            date_components = ["{}_{}".format(date_field, component_value)
                               for component_value in ['year', 'month', 'day']]
            component_values = [int(workgroup_data[component])
                                for component in date_components if component in workgroup_data]
            if len(component_values) == 3:
                clean_data[date_field]= datetime(
                    component_values[0],
                    component_values[1],
                    component_values[2]
                ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        return clean_data

    @classmethod
    def create(cls, name, workgroup_data):
        return workgroup_api.create_workgroup(name, workgroup_data=cls._clean_workgroup_data(workgroup_data), group_object=cls)

    @classmethod
    def list(cls):
        return workgroup_api.get_workgroups(group_object=cls)

    @classmethod
    def fetch(cls, workgroup_id):
        return workgroup_api.get_workgroup(workgroup_id, group_object=cls)

    @classmethod
    def delete(cls, workgroup_id):
        return workgroup_api.delete_workgroup(workgroup_id)

    @classmethod
    def update(cls, workgroup_id, workgroup_data):
        return workgroup_api.update_workgroup(workgroup_id, cls._clean_workgroup_data(workgroup_data), group_object=cls)
