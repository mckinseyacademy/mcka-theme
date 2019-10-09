''' Objects for users / authentication built from json responses from API '''
from .json_object import JsonObject
from . import workgroup_api


class Workgroup(JsonObject):
    # required_fields = ["display_name", "contact_name", "contact_phone", "contact_email", ]

    ''' object representing a organization from api json response '''
    @classmethod
    def create(cls, name, workgroup_data):
        return workgroup_api.create_workgroup(name, workgroup_data=workgroup_data, group_object=cls)

    @classmethod
    def fetch(cls, workgroup_id):
        return workgroup_api.get_workgroup(workgroup_id, group_object=cls)

    @classmethod
    def list(cls):
        return workgroup_api.get_workgroups(group_object=cls)

    @classmethod
    def delete(cls, workgroup_id):
        return workgroup_api.delete_workgroup(workgroup_id)

    @classmethod
    def get_workgroup_users(cls, workgroup_id):
        return workgroup_api.get_workgroup_users(workgroup_id, group_object=cls)

    @classmethod
    def get_workgroup_review_items(cls, workgroup_id):
        return workgroup_api.get_workgroup_review_items(workgroup_id)

    def add_user(self, user_id):
        if workgroup_api.add_user_to_workgroup(self.id, user_id):
            # reload users list
            self.users = Workgroup.get_workgroup_users(self.id)
            return True
        return False

    def add_user_list(self, user_ids):
        for user_id in user_ids:
            workgroup_api.add_user_to_workgroup(self.id, user_id)
        # reload users list
        self.users = Workgroup.get_workgroup_users(self.id)

    def remove_user(self, user_id):
        if workgroup_api.remove_user_from_workgroup(self.id, user_id):
            # reload users list
            self.users = Workgroup.get_workgroup_users(self.id)
            return True
        return False


class Submission(JsonObject):
    date_fields = ["created", "modified"]
