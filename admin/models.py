from api_client import group_api, workgroup_api, organization_api, user_api, course_api
from api_client import group_models, user_models, workgroup_models, organization_models, project_models
from api_client.json_object import JsonObject
from lib.util import DottableDict
from license import controller as license_controller
from django.conf import settings

import hashlib
import random
from datetime import timedelta
from django.utils import timezone
from django.db import models as db_models
from django.dispatch import Signal

GROUP_PROJECT_CATEGORY = 'group-project'
GROUP_PROJECT_V2_CATEGORY = 'gp-v2-project'
GROUP_PROJECT_V2_ACTIVITY_CATEGORY = 'gp-v2-activity'
GROUP_PROJECT_V2_NAVIGATOR_CATEGORY = 'gp-v2-navigator'

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

    NO_PROGRAM_ID = "NO_PROGRAM"

    data_fields = ["display_name", "start_date", "end_date", ]
    date_fields = ["start_date", "end_date"]
    group_type = "series"

    def add_course(self, course_id):
        result = group_api.add_course_to_group(course_id, self.id)
        course_program_event.send(
            sender=self.__class__, course_id=course_id, program_id=self.id, action=ASSOCIATION_ACTIONS.ADD
        )
        return result

    def remove_course(self, course_id):
        result = group_api.remove_course_from_group(course_id, self.id)
        course_program_event.send(
            sender=self.__class__, course_id=course_id, program_id=self.id, action=ASSOCIATION_ACTIONS.REMOVE
        )
        return result

    def fetch_courses(self):
        return group_api.get_courses_in_group(self.id)

    def add_user(self, client_id, user_id):
        group_api.add_user_to_group(user_id, self.id)
        return license_controller.assign_license(self.id, client_id, user_id)

    def remove_user(self, client_id, user_id):
        group_api.remove_user_from_group(user_id, self.id)
        return license_controller.revoke_license(self.id, client_id, user_id)

    @classmethod
    def user_programs_with_course(cls, user_id, course_id):
        return user_api.get_user_groups(user_id, group_type=cls.group_type, group_object=cls, course=course_id)

    @classmethod
    def user_program_list(cls, user_id):
        return user_api.get_user_groups(user_id, group_type=cls.group_type, group_object=cls)

    @classmethod
    def no_program(cls):
        return Program(dictionary={"id": Program.NO_PROGRAM_ID, "name": settings.NO_PROGRAM_NAME})

class ReviewAssignmentGroup(BaseGroupModel):
    data_fields = ["assignment_date", "xblock_id"]
    date_fields = ["assignment_date"]
    group_type = "reviewassignment"

    def add_workgroup(self, workgroup_id):
        return workgroup_api.add_group_to_workgroup(workgroup_id, self.id)

    def add_user(self, user_id):
        return group_api.add_user_to_group(user_id, self.id)

    def remove_user(self, user_id):
        return group_api.remove_user_from_group(user_id, self.id)

    @classmethod
    def list_for_workgroup(cls, workgroup_id, xblock_id=None):
        review_assignment_groups = workgroup_api.get_workgroup_groups(workgroup_id, group_object=cls)
        if xblock_id:
            review_assignment_groups = [rag for rag in review_assignment_groups if rag.xblock_id == xblock_id]
        return review_assignment_groups

class ContactGroup(BaseGroupModel):

    group_type = "contact_group"

class Client(organization_models.Organization):

    def fetch_programs(self):

        groups = [Program.fetch(program_id) for program_id in self.groups]
        programs = [group for group in groups if group.type == "series"]

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

        program_client_event.send(
            sender=self.__class__, client_id=self.id, program_id=program_id, action=ASSOCIATION_ACTIONS.ADD
        )

        return self

    def fetch_students(self):
        users_ids = [str(user_id) for user_id in self.users]
        if users_ids == []:
            return []
        else:
            additional_fields = ["title","city","country","first_name","last_name"]
            return user_api.get_users(ids=users_ids,fields=additional_fields)

    def fetch_students_by_enrolled(self):
        return organization_api.get_users_by_enrolled(self.id, include_course_counts=True)

class WorkGroup(workgroup_models.Workgroup):

    @property
    def user_ids(self):
        return [user.id for user in self.users]

    def fetch_students(self):
        users_ids = [str(user.id) for user in self.users]
        if users_ids == []:
            return []
        else:
            return user_api.get_users(ids=users_ids)

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

class WorkgroupMilestoneDates(JsonObject):
    date_fields = ['upload', 'evaluation', 'grade']

class WorkGroupActivityXBlock(JsonObject):

    required_fields = ['group_reviews_required_count', 'user_review_count', 'milestone_dates']
    object_map = {
        'milestone_dates': WorkgroupMilestoneDates,
    }

    @classmethod
    def fetch_from_uri(cls, uri):
        return course_api.get_module_details(uri, cls.required_fields, cls)

    @classmethod
    def fetch_from_activity(cls, course_id, activity_id):
        activity = course_api.get_course_content_detail(course_id, activity_id)
        if activity.category == GROUP_PROJECT_V2_ACTIVITY_CATEGORY:
            return course_api.get_module_details(activity.uri, cls.required_fields, cls)
        vertical = course_api.get_module_details(activity.children[0].uri)
        return course_api.get_module_details(vertical.children[0].uri, cls.required_fields, cls)

    @property
    def ta_graded(self):
        return self.group_reviews_required_count < 1

class UserRegistrationError(db_models.Model):
    task_key = db_models.CharField(max_length=40, unique=False, db_index=True)
    error = db_models.TextField(default='')

    @classmethod
    def create(cls, error='', task_key=''):
        reg_record = cls.objects.create(error=error, task_key= task_key)
        reg_record.save()

        return reg_record

class UserRegistrationBatch(db_models.Model):
    task_key = db_models.CharField(max_length=40, unique=True, db_index=True)
    attempted = db_models.IntegerField(default=0)
    failed = db_models.IntegerField(default=0)
    succeded = db_models.IntegerField(default=0)
    time_requested = db_models.DateTimeField(default=timezone.now)

    @staticmethod
    def generate_task_key(time):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        return hashlib.sha1(salt+time).hexdigest()

    @classmethod
    def create(cls):
        reg_record = cls.objects.create(attempted=0, failed=0, succeded=0, task_key= cls.generate_task_key(str(timezone.now())))
        reg_record.save()

        return reg_record

    @classmethod
    def clean_old(cls, ErrorModels=UserRegistrationError):
        old_records = cls.objects.filter(time_requested__lte=(timezone.now() - timedelta(days=1)))
        for old_record in old_records:
            old_errors = ErrorModels.objects.filter(task_key=old_record.task_key)
            for old_error in old_errors:
                old_error.delete()
            old_record.delete()
        return True

class ClientNavLinks(db_models.Model):
    class Meta:
        unique_together = ['client_id', 'link_name']

    client_id = db_models.IntegerField(unique=False, db_index=True)
    link_name = db_models.CharField(max_length=200)
    link_label = db_models.CharField(max_length=200)
    link_url= db_models.CharField(max_length=200)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)

class ClientCustomization(db_models.Model):
    client_id = db_models.IntegerField(unique=True, db_index=True)
    hex_notification = db_models.CharField(max_length=7)
    hex_background_bar = db_models.CharField(max_length=7)
    hex_program_name = db_models.CharField(max_length=7)
    hex_navigation_icons = db_models.CharField(max_length=7)
    hex_course_title = db_models.CharField(max_length=7)
    hex_page_background = db_models.CharField(max_length=7)

ROLE_ACTIONS = DottableDict(
    GRANT='grant',
    REVOKE='revoke'
)

ASSOCIATION_ACTIONS = DottableDict(
    ADD='add',
    REMOVE='remove'
)

internal_admin_role_event = Signal(providing_args=['user_id', 'action'])
course_program_event = Signal(providing_args=['course_id', 'program_id', 'action'])
program_client_event = Signal(providing_args=['client_id', 'program_id', 'action'])
