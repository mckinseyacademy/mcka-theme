from api_client import group_api
from api_client import group_models, user_models
from license import controller as license_controller
from django.conf import settings

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

    def add_user(self, client_id, user_id):
        return license_controller.assign_license(self.id, client_id, user_id)

    @classmethod
    def programs_with_course(cls, course_id):
        programs = [program for program in cls.list() if course_id in [course.course_id for course in program.fetch_courses()]]
        if not programs:
            programs = []

        return programs


class Client(BaseGroupModel):
    data_fields = ["display_name", "contact_name", "phone", "email", ]
    group_type = "organization"

    def fetch_students(self):
        return self.get_users()

    def fetch_programs(self):
        groups = self.get_groups(params=[{'key': 'type', 'value': 'series'}])
        programs = [Program.fetch(group.id) for group in groups]
        for program in programs:
            try:
                program.places_allocated, program.places_assigned = license_controller.licenses_report(program.id, self.id)
            except:
                program.places_allocated = None
                program.places_assigned = None

        return programs

    def add_program(self, program_id, places):
        # Add program group to this client
        group_info = group_api.add_group_to_group(program_id, self.id)

        # set up licenses
        license_controller.create_licenses(program_id, self.id, places)

        return group_info

class WorkGroup(BaseGroupModel):
    data_fields = ["privacy", 'client_id', ]
    group_type = "workgroup"

    def fetch_students(self):
        return self.get_users()

    def add_to_course(self, course_id):
        return group_api.add_group_to_course_content(self.id, course_id)

    @classmethod
    def fetch_with_members(cls, workgroup_id):
        workgroup = cls.fetch(workgroup_id)
        workgroup.members = workgroup.fetch_students()
        workgroup.teaching_assistant = user_models.UserResponse(dictionary={
            "username": "ta",
            "full_name": "Your TA",
            "title": "Teaching Assistant",
            "email": settings.TA_EMAIL_GROUP,
        })

        return workgroup

    def add_workgroup_to_client(self, client_id):
        return group_api.add_group_to_group(self.id, client_id)
