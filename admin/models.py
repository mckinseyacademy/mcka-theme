from api_client import group_api, workgroup_api, organization_api, user_api, course_api
from api_client import group_models, user_models, workgroup_models, organization_models, project_models
from api_client.json_object import JsonObject
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
        group_api.add_user_to_group(user_id, self.id)
        return license_controller.assign_license(self.id, client_id, user_id)

    @classmethod
    def user_programs_with_course(cls, user_id, course_id):
        return user_api.get_user_groups(user_id, group_type=cls.group_type, group_object=cls, course=course_id)

class ReviewAssignmentGroup(BaseGroupModel):
    data_fields = ["assignment_date", "xblock_id"]
    date_fields = ["assignment_date"]
    group_type = "reviewassignment"

    def add_workgroup(self, workgroup_id):
        return workgroup_api.add_group_to_workgroup(workgroup_id, self.id)

    def add_user(self, user_id):
        return group_api.add_user_to_group(user_id, self.id)

    @classmethod
    def list_for_workgroup(cls, workgroup_id):
        return [cls.fetch(rag.id) for rag in workgroup_api.get_workgroup_groups(workgroup_id)]


class Client(organization_models.Organization):

    def fetch_programs(self):
        programs = [Program.fetch(program_id) for program_id in self.groups]
        for program in programs:
            try:
                program.places_allocated, program.places_assigned = license_controller.licenses_report(program.id, self.id)
            except:
                program.places_allocated = None
                program.places_assigned = None

        return programs

    def add_program(self, program_id, places):
        # Add program group to this client
        self.add_group(int(program_id))

        # set up licenses
        license_controller.create_licenses(program_id, self.id, places)

        return self

    def fetch_students(self):
        users_ids = [str(user_id) for user_id in self.users]
        if users_ids == []:
            return []
        else:
            return user_api.get_users(ids=','.join(users_ids))

    def fetch_students_by_enrolled(self):
        return organization_api.get_users_by_enrolled(self.id)

class ClientList(organization_models.OrganizationList):
    object_map = {
        "results": Client
    }

class WorkGroup(workgroup_models.Workgroup):

    @property
    def user_ids(self):
        return [user.id for user in self.users]

    def fetch_students(self):
        users_ids = [str(user.id) for user in self.users]
        if users_ids == []:
            return []
        else:
            return user_api.get_users(ids=','.join(users_ids))

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

class WorkGroupActivityXBlock(JsonObject):

    required_fields = ['group_reviews_required_count', 'user_review_count']

    @classmethod
    def fetch_from_uri(cls, uri):
        return course_api.get_module_details(uri, cls.required_fields, cls)

    @classmethod
    def fetch_from_activity(cls, course_id, activity_id):
        activity = course_api.get_course_content_detail(course_id, activity_id)
        vertical = course_api.get_module_details(activity.children[0].uri)
        return course_api.get_module_details(vertical.children[0].uri, cls.required_fields, cls)

    @property
    def ta_graded(self):
        return self.group_reviews_required_count < 1

