import json

from api_client import group_api, workgroup_api, organization_api, user_api, course_api
from api_client import group_models, user_models, workgroup_models, organization_models

from api_client.json_object import JsonObject
from lib.utils import DottableDict
from license import controller as license_controller
from django.conf import settings

import hashlib
import random
from datetime import timedelta
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import models as db_models
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from api_client.group_api import TAG_GROUPS

GROUP_PROJECT_CATEGORY = 'group-project'
GROUP_PROJECT_V2_CATEGORY = 'gp-v2-project'
GROUP_PROJECT_V2_ACTIVITY_CATEGORY = 'gp-v2-activity'
GROUP_PROJECT_V2_GRADING_STAGES = ['gp-v2-stage-peer-review']
OTHER_ROLE = "Other"


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
        # course_program_event.send(
        #     sender=self.__class__, course_id=course_id, program_id=self.id, action=ASSOCIATION_ACTIONS.ADD
        # )
        return result

    def remove_course(self, course_id):
        result = group_api.remove_course_from_group(course_id, self.id)
        # course_program_event.send(
        #     sender=self.__class__, course_id=course_id, program_id=self.id, action=ASSOCIATION_ACTIONS.REMOVE
        # )
        return result

    def fetch_courses(self):
        return group_api.get_courses_in_group(self.id)

    def add_user(self, client_id, user_id):
        group_api.add_users_to_group([user_id], self.id)
        return license_controller.assign_license(self.id, client_id, user_id)

    def remove_user(self, client_id, user_id):
        group_api.remove_user_from_group(user_id, self.id)
        return license_controller.revoke_license(self.id, client_id, user_id)

    @classmethod
    def user_programs_with_course(cls, user_id, course_id):
        return user_api.get_user_groups(user_id, group_type=cls.group_type, parse_object=cls, course=course_id)

    @classmethod
    def user_program_list(cls, user_id):
        return user_api.get_user_groups(user_id, group_type=cls.group_type, parse_object=cls)

    @classmethod
    def no_program(cls):
        return Program(dictionary={"id": Program.NO_PROGRAM_ID, "name": settings.NO_PROGRAM_NAME})

    def __eq__(self, other):
        if not isinstance(other, Program):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "<{module_name}.{class_name}>: {id}>".format(
            module_name=__name__,
            class_name=self.__class__.__name__, id=self.id
        )

    def __unicode__(self):
        return unicode(str(self))

    def __repr__(self):
        return unicode(self)


class Tag(BaseGroupModel):

    '''
    Tags are edx groups for tagging course. Group types for tags are in TAG_GROUPS.
    '''

    group_type = TAG_GROUPS.COMMON

    def get_courses(self):
        return group_api.get_courses_in_group(self.id)

    def add_course(self, course_id):
        return group_api.add_course_to_group(course_id, self.id)

    def remove_course(self, course_id):
        return group_api.remove_course_from_group(course_id, self.id)

    def add_internal_course(self, course_id):
        response = group_api.add_course_to_group(course_id, self.id)
        internal_course_event.send(
            sender=self.__class__, course_id=course_id, action=ASSOCIATION_ACTIONS.ADD
        )
        return response

    def remove_internal_course(self, course_id):
        response = group_api.remove_course_from_group(course_id, self.id)
        internal_course_event.send(
            sender=self.__class__, course_id=course_id, action=ASSOCIATION_ACTIONS.REMOVE
        )
        return response

    @classmethod
    def fetch_all(cls):
        tags = []
        for tag_type in TAG_GROUPS:
            cls.group_type = TAG_GROUPS[tag_type]
            tags.extend(cls.list())
        return tags

    @classmethod
    def create_internal(cls, tag_name, tag_data):
        cls.group_type = TAG_GROUPS.INTERNAL
        return cls.create(tag_name, tag_data)

    @classmethod
    def course_tags(cls, course_id):
        group_type = ",".join(TAG_GROUPS.values())
        tags = course_api.get_course_groups(course_id=course_id, group_type=group_type)
        return tags


class ReviewAssignmentGroup(BaseGroupModel):
    data_fields = ["assignment_date", "xblock_id"]
    date_fields = ["assignment_date"]
    group_type = "reviewassignment"

    def add_workgroup(self, workgroup_id):
        return workgroup_api.add_group_to_workgroup(workgroup_id, self.id)

    def add_user(self, user_id):
        return group_api.add_users_to_group([user_id], self.id)

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
                program.places_assigned, license = license_controller.licenses_report(program.id, self.id)
                program.places_allocated = len(license)
            except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
                program.places_allocated = None
                program.places_assigned = None

        return programs

    def add_program(self, program_id, places):
        # Add program group to this client
        self.add_group(int(program_id))

        # set up licenses
        license_controller.create_licenses(program_id, self.id, places)

        # program_client_event.send(
        #     sender=self.__class__, client_id=self.id, program_id=program_id, action=ASSOCIATION_ACTIONS.ADD
        # )

        return self

    def fetch_students(self):
        users_ids = [str(user_id) for user_id in self.users]
        if users_ids == []:
            return []
        else:
            additional_fields = ["title", "city", "country", "first_name", "last_name"]
            return user_api.get_users(ids=users_ids, fields=additional_fields)

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
        workgroup.teaching_assistant = user_models.SimpleUserResponse(dictionary={
            "username": "ta",
            "full_name": "Your TA",
            "title": "Teaching Assistant",
            "email": settings.TA_EMAIL_GROUP,
        })

        return workgroup


class WorkgroupMilestoneDates(JsonObject):
    date_fields = ['upload', 'evaluation', 'grade']


class WorkGroupV2StageXBlock(JsonObject):
    required_fields = ['close_date']
    date_fields = ['close_date']

    @classmethod
    def fetch_from_uri(cls, uri):
        return course_api.get_module_details(uri, cls.required_fields, cls)


class WorkGroupActivityXBlock(JsonObject):
    required_fields = ['group_reviews_required_count', 'user_review_count', 'milestone_dates', 'weight', 'due_date']
    date_fields = ['due_date']
    object_map = {
        'milestone_dates': WorkgroupMilestoneDates
    }

    @classmethod
    def fetch_from_uri(cls, uri):
        return course_api.get_module_details(uri, cls.required_fields, cls)

    @classmethod
    def fetch_from_activity(cls, course_id, activity_id, is_v2_project=False):
        # v2 projects contain activities of v2 category so skip two calls
        if is_v2_project:
            return course_api.get_course_content_detail(course_id, activity_id, cls.required_fields, cls)

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
    user_email = db_models.CharField(max_length=200, null=True, blank=True)
    user_data = db_models.TextField(null=True, blank=True)


class UserRegistrationBatch(db_models.Model):
    task_key = db_models.CharField(max_length=40, unique=True, db_index=True)
    attempted = db_models.IntegerField(default=0)
    failed = db_models.IntegerField(default=0)
    succeded = db_models.IntegerField(default=0)
    time_requested = db_models.DateTimeField(default=timezone.now)
    error_file_url = db_models.CharField(max_length=200, null=True)
    activation_file_url = db_models.CharField(max_length=200, null=True)
    uploaded_file_name = db_models.CharField(max_length=200, null=True)
    time_completed = db_models.DateTimeField(null=True, default=None)
    triggered_by = db_models.CharField(max_length=200, null=True)

    @staticmethod
    def generate_task_key(time):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        return hashlib.sha1(salt+time).hexdigest()

    @classmethod
    def create(cls):
        reg_record = cls.objects.create(attempted=0, failed=0, succeded=0,
                                        task_key=cls.generate_task_key(str(timezone.now())))
        reg_record.save()

        return reg_record


class BatchOperationErrors(db_models.Model):
    task_key = db_models.CharField(max_length=40, unique=False, db_index=True)
    error = db_models.TextField(default='')
    user_id = db_models.IntegerField(default=0)

    @classmethod
    def create(cls, error='', task_key='', user_id=0):
        reg_record = cls.objects.create(error=error, task_key=task_key, user_id=user_id)
        reg_record.save()

        return reg_record


class BatchOperationStatus(db_models.Model):
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
        reg_record = cls.objects.create(attempted=0, failed=0, succeded=0,
                                        task_key=cls.generate_task_key(str(timezone.now())))
        reg_record.save()

        return reg_record

    @classmethod
    def clean_old(cls, ErrorModels=BatchOperationErrors):
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
    link_url = db_models.CharField(max_length=200)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)


class ClientCustomization(db_models.Model):
    client_id = db_models.IntegerField(unique=True, db_index=True)
    hex_notification = db_models.CharField(max_length=7)
    hex_notification_text = db_models.CharField(max_length=7)
    hex_background_bar = db_models.CharField(max_length=7)
    hex_program_name = db_models.CharField(max_length=7)
    hex_navigation_icons = db_models.CharField(max_length=7)
    hex_course_title = db_models.CharField(max_length=7)
    hex_page_background = db_models.CharField(max_length=7)
    client_logo = db_models.CharField(max_length=200)
    identity_provider = db_models.CharField(blank=True, max_length=200)
    client_background = db_models.CharField(max_length=200)
    client_background_css = db_models.CharField(max_length=200)
    global_client_logo = db_models.CharField(max_length=200, blank=True)
    hex_background_main_navigation = db_models.CharField(max_length=7, blank=True)
    new_ui_enabled = db_models.BooleanField(default=True)
    new_ui_enabled_at = db_models.DateTimeField(auto_now_add=True)
    is_footer_enabled = db_models.BooleanField(default=True)

    def delete(self):
        images = (
            'client_logo',
            'client_background',
            'global_client_logo'
        )
        for image in images:
            image_url = getattr(self, image).replace('/accounts/', '')
            if image_url and default_storage.exists(image_url):
                default_storage.delete(image_url)
        super(ClientCustomization, self).delete()


class CompanyInvoicingDetails(db_models.Model):
    company_id = db_models.IntegerField(unique=True, db_index=True)
    full_name = db_models.CharField(max_length=200, blank=True)
    title = db_models.CharField(max_length=200, blank=True)
    address1 = db_models.CharField(max_length=200, blank=True)
    address2 = db_models.CharField(max_length=200, blank=True)
    city = db_models.CharField(max_length=200, blank=True)
    state = db_models.CharField(max_length=200, blank=True)
    postal_code = db_models.CharField(max_length=200, blank=True)
    country = db_models.CharField(max_length=200, blank=True)
    po = db_models.CharField(max_length=200, blank=True)
    identity_provider = db_models.CharField(blank=True, max_length=200)


class CompanyContact(db_models.Model):
    class Meta:
        unique_together = ['company_id', 'contact_type']

    COMPANY_CONTACT_TYPE_CHOICES = (
        (u'0', _('Executive Sponsor')),
        (u'1', _('IT Security Contact')),
        (u'2', _('Senior HR/PD Professional')),
        (u'3', _('Day-to-Day Coordinator')),
    )

    company_id = db_models.IntegerField(db_index=True)
    contact_type = db_models.CharField(max_length=1, choices=COMPANY_CONTACT_TYPE_CHOICES)
    full_name = db_models.CharField(max_length=200, blank=True)
    title = db_models.CharField(max_length=200, blank=True)
    email = db_models.CharField(max_length=200, blank=True)
    phone = db_models.CharField(max_length=200, blank=True)

    TYPE_DESCRIPTION = {
        u'0': _('Senior executive sponsoring McKinsey Academy program within company'),
        u'1': _('IT department contact to troubleshoot technical issues (e.g., corporate firewalls, whitelisting)'),
        u'2': _('Overseeing/coordinating Academy program with broader people strategy'),
        u'3': _('Individual managing day-to-day operation of the program (e.g., missing participant information, '
                'engagement)')
    }

    @classmethod
    def get_type_description(cls, contact_type):
        return cls.TYPE_DESCRIPTION[contact_type]

    @classmethod
    def get_contact_type(cls, contact_type):
        return cls.COMPANY_CONTACT_TYPE_CHOICES[contact_type][1]


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
internal_course_event = Signal(providing_args=['course_id', 'action'])
new_internal_admin_event = Signal(providing_args=['user_id', 'action'])


class AccessKey(db_models.Model):
    """
    A generated access code that can is used for student registration and enrollment.
    """
    code = db_models.CharField(max_length=50, unique=True)
    client_id = db_models.IntegerField()
    course_id = db_models.CharField(blank=True, max_length=200)
    program_id = db_models.IntegerField(null=True, blank=True)
    name = db_models.CharField(blank=False, max_length=200)
    disabled = db_models.BooleanField(default=False)
    expiration_date = db_models.DateTimeField(null=True, blank=True)
    user_count = db_models.IntegerField(default=0, blank=True)


class DashboardAdminQuickFilter(db_models.Model):
    """
    Represents a single "Quick Link Filter" that is a saved filter that
    pre-filters dashboard. Quick links are saved on per-user basis.

    Notes:

        Following columns should be considered unique together:
        (user_id, program_id, course_id, company_id, group_work_project_id)
        This is enforced by DashboardAdminQuickFilterForm.

        Due to how mysql handles unique constraint adding Meta.unique_together
        wouldn't work for rows containing nulls --- row with nulls in any
        of the beforementioned columns could be duplicated.

        See this for details: http://bugs.mysql.com/bug.php?id=25544.
        Since having duplicates is not a major problem (but a rather minor
        usability issue) instead of working around this MySQL feature
        it was decided to add this comment.

    """

    date_created = db_models.DateTimeField(auto_now=True, db_index=True)
    user_id = db_models.IntegerField(null=False, db_index=True)
    program_id = db_models.IntegerField(null=False)
    course_id = db_models.CharField(null=True, blank=True, max_length=200)
    company_id = db_models.IntegerField(null=True, blank=True)
    group_work_project_id = db_models.CharField(null=True, max_length=300, blank=True)

    class Meta:
        ordering = ('date_created', )
        # Following columns should be considered unique together:
        # (user_id, program_id, course_id, company_id, group_work_project_id)
        # see notes in the class docstring for details.


class BrandingSettings(db_models.Model):

    background_image = db_models.ImageField(upload_to=settings.LEARNER_DASHBOARD_BACKGROUND_IMAGE, blank=True)
    logo_image = db_models.ImageField(upload_to=settings.LEARNER_DASHBOARD_LOGO_IMAGE, blank=True)
    rule_color = db_models.CharField(settings.LEARNER_DASHBOARD_RULE_COLOR, max_length=20, blank=True)
    icon_color = db_models.CharField(settings.LEARNER_DASHBOARD_ICON_COLOR, max_length=20, blank=True)
    discover_title_color = db_models.CharField(max_length=20, blank=True, default=settings.DISCOVER_TITLE_COLOR)
    discover_author_color = db_models.CharField(max_length=20, blank=True, default=settings.DISCOVER_AUTHOR_COLOR)
    discover_rule_color = db_models.CharField(max_length=20, blank=True, default=settings.DISCOVER_RULE_COLOR)
    background_color = db_models.CharField(max_length=20, blank=True,
                                           default=settings.LEARNER_DASHBOARD_BACKGROUND_COLOR)
    top_bar_color = db_models.CharField(max_length=20, blank=True, default=settings.LEARNER_DASHBOARD_TOP_BAR_COLOR)

    TYPES = (
        (u'1', u'Normal'),
        (u'2', u'Tiled'),
        (u'3', u'Stretched')
    )
    background_style = db_models.CharField(max_length=1, choices=TYPES, blank=True)

    client_id = db_models.IntegerField(blank=False, unique=True)


class LearnerDashboard(db_models.Model):

    title = db_models.CharField(blank=True, max_length=80)
    description = db_models.CharField(blank=True, max_length=5000)

    title_color = db_models.CharField(max_length=20, blank=True, default=settings.LEARNER_DASHBOARD_TITLE_COLOR)
    description_color = db_models.CharField(max_length=20, blank=True,
                                            default=settings.LEARNER_DASHBOARD_DESCRIPTION_COLOR)

    client_id = db_models.IntegerField(null=True)
    course_id = db_models.CharField(blank=False, max_length=500, db_index=True)


class LearnerDashboardTile(db_models.Model):

    label = db_models.CharField(max_length=20, blank=True)
    title = db_models.CharField(blank=True, max_length=40)
    link = db_models.CharField(blank=False, max_length=500)
    note = db_models.CharField(blank=True, max_length=40)
    details = db_models.CharField(blank=True, max_length=200)
    location = db_models.CharField(blank=True, max_length=200)
    download_link = db_models.URLField(blank=True, null=True)

    fa_icon = db_models.CharField(blank=True, max_length=20)
    position = db_models.IntegerField(blank=False, default=100)

    show_in_calendar = db_models.BooleanField(default=False)
    show_in_dashboard = db_models.BooleanField(default=True)
    track_progress = db_models.BooleanField(default=True)
    hidden_from_learners = db_models.BooleanField(default=False)

    start_date = db_models.DateTimeField(null=True, blank=True)
    end_date = db_models.DateTimeField(null=True, blank=True)
    publish_date = db_models.DateTimeField(null=True, blank=True)

    background_image = db_models.ImageField(upload_to=settings.TILE_BACKGROUND_IMAGE, blank=True)
    label_color = db_models.CharField(max_length=20, default=settings.TILE_LABEL_COLOR, blank=True)
    title_color = db_models.CharField(max_length=20, default=settings.TILE_TITLE_COLOR, blank=True)
    note_color = db_models.CharField(max_length=20, default=settings.TILE_NOTE_COLOR, blank=True)
    tile_background_color = db_models.CharField(max_length=20, default=settings.TILE_BACKGROUND_COLOR, blank=True)

    TYPES = (
        (u'1', _('Article')),
        (u'2', _('Lesson')),
        (u'3', _('Module')),
        (u'4', _('Course')),
        (u'5', _('In Person Session')),
        (u'6', _('Webinar')),
        (u'7', _('Group work')),
    )
    tile_type = db_models.CharField(max_length=1, choices=TYPES)

    ROW = (
        (u'1', u'1'),
        (u'2', u'2'),
        (u'3', u'3'),
        (u'4', u'4'),
        (u'5', u'5')
    )
    row = db_models.CharField(max_length=1, choices=ROW, blank=True)

    learner_dashboard = db_models.ForeignKey(
        'LearnerDashboard',
        on_delete=db_models.CASCADE,
    )


class LearnerDashboardDiscovery(db_models.Model):

    link = db_models.URLField(blank=True, null=True)
    title = db_models.CharField(blank=True, null=True, max_length=5000)
    author = db_models.CharField(blank=True, null=True, max_length=5000)
    position = db_models.IntegerField(default=100)

    learner_dashboard = db_models.ForeignKey(
        'LearnerDashboard',
        on_delete=db_models.CASCADE,
    )


class LearnerDashboardBranding(db_models.Model):

    background_image = db_models.ImageField(upload_to=settings.LEARNER_DASHBOARD_BACKGROUND_IMAGE, blank=True)
    logo_image = db_models.ImageField(upload_to=settings.LEARNER_DASHBOARD_LOGO_IMAGE, blank=True)
    rule_color = db_models.CharField(settings.LEARNER_DASHBOARD_RULE_COLOR, max_length=20, blank=True)
    icon_color = db_models.CharField(settings.LEARNER_DASHBOARD_ICON_COLOR, max_length=20, blank=True)
    discover_title_color = db_models.CharField(max_length=20, blank=True, default=settings.DISCOVER_TITLE_COLOR)
    discover_author_color = db_models.CharField(max_length=20, blank=True, default=settings.DISCOVER_AUTHOR_COLOR)
    discover_rule_color = db_models.CharField(max_length=20, blank=True, default=settings.DISCOVER_RULE_COLOR)
    background_color = db_models.CharField(max_length=20, blank=True,
                                           default=settings.LEARNER_DASHBOARD_BACKGROUND_COLOR)
    top_bar_color = db_models.CharField(max_length=20, blank=True, default=settings.LEARNER_DASHBOARD_TOP_BAR_COLOR)

    TYPES = (
        (u'1', u'Normal'),
        (u'2', u'Tiled'),
        (u'3', u'Stretched')
    )
    background_style = db_models.CharField(max_length=1, choices=TYPES, blank=True)

    learner_dashboard = db_models.ForeignKey(
        'LearnerDashboard',
        on_delete=db_models.CASCADE,
    )


class EmailTemplate(db_models.Model):
    title = db_models.CharField(blank=False, null=False, max_length=64)
    subject = db_models.CharField(blank=False, null=False, max_length=256)
    body = db_models.TextField(blank=False, null=False,)

    @classmethod
    def create(cls, title, subject, body):
        email_template = cls(title=title, subject=subject, body=body)
        return email_template


class TileBookmark(db_models.Model):
    user = db_models.IntegerField(blank=False, unique=True)
    lesson_link = db_models.CharField(blank=True, null=True, max_length=2000)

    tile = db_models.ForeignKey(
        'LearnerDashboardTile',
        on_delete=db_models.CASCADE,
    )
    learner_dashboard = db_models.ForeignKey(
        'LearnerDashboard',
        on_delete=db_models.CASCADE,
    )


class LearnerDashboardTileProgress(db_models.Model):

    user = db_models.IntegerField(blank=False, null=False)

    PROGRESS_TYPES = (
        (u'1', _('Not Started')),
        (u'2', _('In Progress')),
        (u'3', _('Complete')),
        (u'3', _('Incomplete'))
    )
    progress = db_models.CharField(max_length=1, choices=PROGRESS_TYPES, blank=True, null=True)
    percentage = db_models.IntegerField(blank=True, null=True)

    milestone = db_models.ForeignKey(
        'LearnerDashboardTile',
        on_delete=db_models.CASCADE,
    )


class CourseRun(db_models.Model):

    name = db_models.SlugField(max_length=50, blank=False, unique=True)
    max_participants = db_models.IntegerField(blank=True, null=True)
    total_participants = db_models.IntegerField(blank=True, null=True, default=0)
    total_activations_sent = db_models.IntegerField(blank=True, null=True, default=0)
    is_open = db_models.BooleanField(default=True)
    course_id = db_models.CharField(blank=False, null=False, max_length=500)
    access_key_link = db_models.URLField(blank=True, null=True)
    email_template_new = db_models.CharField(blank=False, null=False, max_length=2000)
    email_template_existing = db_models.CharField(blank=False, null=False, max_length=2000)
    email_template_mcka = db_models.CharField(blank=False, null=False, max_length=2000)
    email_template_closed = db_models.CharField(blank=False, null=False, max_length=2000)
    self_registration_page_heading = db_models.CharField(blank=False, null=False, max_length=2000,
                                                         default="Self Registration Page Heading")
    self_registration_description_text = db_models.CharField(blank=False, null=False, max_length=2000,
                                                             default="Self Registration Description Text")


class SelfRegistrationRoles(db_models.Model):
    course_run = db_models.ForeignKey(
        'CourseRun',
        on_delete=db_models.CASCADE,
    )
    option_text = db_models.CharField(blank=False, null=False, max_length=500)

    def __unicode__(self):
        return self.option_text


@receiver(post_save, sender=CourseRun)
def create_self_reg_other_role(sender, instance, created, **kwargs):

    if created:
        SelfRegistrationRoles.objects.create(course_run=instance, option_text=OTHER_ROLE)


class AdminTask(db_models.Model):
    """
    Model to represent a status for an admin task.
    """
    task_id = db_models.CharField(max_length=255, blank=False, null=False)
    course_id = db_models.CharField(max_length=255, blank=True, null=True)
    parameters = db_models.CharField(max_length=2048, blank=True, null=True)
    task_type = db_models.CharField(max_length=512, blank=False, null=False)
    output = db_models.TextField(blank=True, null=True)
    status = db_models.CharField(max_length=215, blank=False, null=False, default='PROGRESS')
    username = db_models.CharField(max_length=512, blank=True, null=True)
    requested_datetime = db_models.DateTimeField(auto_now_add=True)

    @property
    def task_output(self):
        """task output -> json.loads(self.output)"""
        output = self.output or '{}'
        try:
            output = json.loads(output)
        except ValueError:
            # Invalid JSON obj.
            output = {'output': output}
        return output

    @property
    def task_parameters(self):
        """task parameters -> json.loads(self.parameters)"""
        params = self.parameters or '{}'
        try:
            params = json.loads(params)
        except ValueError:
            # Invalid JSON obj
            params = {'params': params}
        return params

    class Meta:
        indexes = [
            db_models.Index(fields=['task_id']),
            db_models.Index(fields=['course_id']),
        ]

    def __str__(self):
        """Str -> self.task_id, self.course_id, self.status"""
        return '{task_id}: {course_id} - {status}'.format(
            task_id=self.task_id,
            course_id=self.course_id,
            status=self.status
        )

    def __repr__(self):
        """Repr -> self.task_id, self.course_id, self.status"""
        return 'AdminTask({task_id}, {course_id}, {status})'.format(
            task_id=self.task_id,
            course_id=self.course_id,
            status=self.status
        )


class DeletionAdmin(db_models.Model):
    """
    Model to store emails that should be cc'ed on emails.
    """
    email = db_models.CharField(max_length=255, blank=False, null=False, unique=True)
