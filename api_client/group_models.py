''' Objects for users / authentication built from json responses from API '''
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

    @classmethod
    def create(cls, name, data):
        clean_data = {
            key: value for key, value in data.iteritems() if key in cls.data_fields
        }
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
