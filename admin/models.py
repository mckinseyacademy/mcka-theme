from api_client import group_api
from api_client import group_models


class BaseGroupModel(group_models.GroupInfo):

    def __init__(self, json_data=None, dictionary=None):
        super(BaseGroupModel, self).__init__(
            json_data=json_data,
            dictionary=dictionary
        )

        if not hasattr(self, "id") and hasattr(self, "group_id"):
            self.id = self.group_id

        if not hasattr(self, "display_name") and hasattr(self, "name"):
            self.display_name = self.name

    def __unicode__(self):
        return self.name


class Program(BaseGroupModel):
    data_fields = ["display_name", "start_date", "end_date", ]
    date_fields = ["start_date", "end_date"]
    group_type = "series"

    def add_course(self, course_id):
        return group_api.add_course_to_group(course_id, self.id)

    def fetch_courses(self):
        return group_api.get_courses_in_group(self.id)

    def add_user(self, user_id):
        return group_api.add_user_to_group(user_id, self.id)


class Client(BaseGroupModel):
    data_fields = ["display_name", "contact_name", "phone", "email", ]
    group_type = "organization"

    def fetch_students(self):
        return self.get_users()

    def fetch_programs(self):
        # Would be nice to filter groups based upon their group type, but we
        # don't have that available in results yet
        groups = self.get_groups()
        programs = []
        for group in groups:
            # we will filter later, so we protect ourselves against
            # non-programs herein
            try:
                programs.append(Program.fetch(group.id))
            except:
                pass

        return programs

    def add_program(self, program_id):
        return group_api.add_group_to_group(program_id, self.id)
