''' Objects for users / authentication built from json responses from API '''
from datetime import date
from .json_object import JsonObject
import group_api


class GroupInfo(JsonObject):

    ''' object representing a group from api json response '''
    #required_fields = ["name", "id"]
    data_fields = []
    group_type = None

    def __init__(self, json_data=None, dictionary=None):
        super(GroupInfo, self).__init__(
            json_data=json_data,
            dictionary=dictionary
        )

        # has additional attributes in embedded data
        if hasattr(self, "data"):
            for data_attr in self.data_fields:
                if hasattr(self.data, data_attr):
                    setattr(
                        self,
                        data_attr,
                        getattr(self.data, data_attr, None)
                    )

    def get_users(self):
        return group_api.get_users_in_group(self.id)

    def get_groups(self):
        return group_api.get_groups_in_group(self.id)

    @classmethod
    def create(cls, name, data):
        clean_data = {
            key: value for key, value in data.iteritems() if key in cls.data_fields
        }

        for date_field in cls.date_fields:
            date_components = ["{}_{}".format(date_field, component_value)
                               for component_value in ['year', 'month', 'day']]
            component_values = [data[component]
                                for component in date_components if component in data]
            if len(component_values) == 3:
                clean_data[date_field] = "{}-{}-{}T00:00:00.00000Z".format(
                    component_values[0],
                    component_values[1],
                    component_values[2],
                )

        return group_api.create_group(name, cls.group_type, group_data=clean_data, group_object=cls)

    @classmethod
    def list(cls):
        return group_api.get_groups_of_type(cls.group_type, group_object=cls)

    @classmethod
    def fetch(cls, group_id):
        return group_api.fetch_group(group_id, group_object=cls)

    @classmethod
    def delete(cls, group_id):
        return group_api.delete_group(group_id)
