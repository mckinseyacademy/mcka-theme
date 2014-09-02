''' Objects for courses built from json responses from API '''
import datetime
import math

from django.conf import settings
from django.utils.translation import ugettext as _

from .json_object import CategorisedJsonObject, JsonObject

# Temporary id converter to fix up problems post opaque keys
from lib.util import LegacyIdConvert

# Create your models here.

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods

class _HasDueDate(CategorisedJsonObject):
    date_fields = ["due"]

    @property
    def due_upon(self):
        due_date = self.due_date
        if due_date is None:
            return "-"
        return due_date.strftime(settings.DATE_DISPLAY_FORMAT)

    @property
    def due_date(self):
        if not self.due is None:
            return self.due

        if not hasattr(self, "children"):
            return None

        last_child_due_date = None
        for ch in self.children:
            child_due = ch.due_date if hasattr(ch, "due_date") else ch.due
            if not child_due is None:
                if last_child_due_date is None or child_due > last_child_due_date:
                    last_child_due_date = child_due

        return last_child_due_date

class Page(_HasDueDate):

    ''' object representing a page / module within a subsection '''
    required_fields = ["id", "name", ]

    def vertical_usage_id(self):
        # Convert to old model
        page_id = LegacyIdConvert.legacy_from_new(self.id)
        return page_id.replace('/', ';_')

    def child_category_list(self):
        if not hasattr(self, "children"):
            return []

        return [child.category for child in self.children]

class Sequential(_HasDueDate):

    ''' object representing a subsection within a chapter / lesson '''
    required_fields = ["id", "name", ]

class Chapter(_HasDueDate):

    ''' object representing a chapter / lesson within a course '''
    required_fields = ["id", "name", ]

class Course(CategorisedJsonObject):

    ''' object representing a course '''
    required_fields = ["id", "name", ]
    date_fields = ["start", "end",]

    @property
    def nav_url(self):
        return '/courses/{}'.format(self.id)

    @property
    def formatted_start_date(self):
        if hasattr(self, 'start') and not self.start is None:
            return "{} {}".format(
                _("Available"),
                self.start.strftime(settings.DATE_DISPLAY_FORMAT)
            )
        return None

    @property
    def percent_complete_message(self):
        if hasattr(self, 'percent_complete'):
            return "{}% {}".format(
                self.percent_complete,
                _("complete")
            )
        return ""

    @property
    def started(self):
        return int(self.days_till_start) < 1

    @property
    def ended(self):
        return int(self.days_till_end) < 0

    @property
    def days_till_start(self):
        if not getattr(self, 'start', None) is None:
            delta = self.start - datetime.datetime.today()
            return delta.days
        return 0

    @property
    def days_till_end(self):
        if not getattr(self, 'end', None) is None:
            delta = self.end - datetime.datetime.today()
            return delta.days
        return 0

    def module_count(self):
        module_count = 0
        for chapter in self.chapters:
            for sequential in chapter.sequentials:
                module_count += len(sequential.children)

        return module_count

    def components_ids(self, filter_out_categories=[]):
        components = []
        for lesson in self.chapters:
            for sequential in lesson.sequentials:
                for page in sequential.pages:
                    components.extend([child.id for child in page.children if child.category not in filter_out_categories])
        return components

    def lesson_component_ids(self, lesson_id, completions=None, filter_out_categories=[]):
        components = []
        try:
            lesson = [lesson for lesson in self.chapters if lesson.id == lesson_id][0]
            for sequential in lesson.sequentials:
                for module in sequential.pages:
                    children = [child.id for child in module.children if child.category not in filter_out_categories]
                    components.extend(children)
                    if completions:
                        completed = set(completions).intersection(children)
                        module.is_complete = len(completed) == len(children)
            return components
        except:
            return components

    def get_current_sequential(self, lesson_id, module_id):
        try:
            lesson = [lesson for lesson in self.chapters if lesson.id == lesson_id][0]
            for sequential in lesson.sequentials:
                if len([module for module in sequential.pages if module.id == module_id]) > 0:
                    return sequential
        except:
            return None

class CourseListCourse(JsonObject):
    required_fields = ["course_id", "display_name", ]

class CourseList(JsonObject):
    object_map = {
        "courses": CourseListCourse
    }

class CourseEnrollment(JsonObject):
    ''' object representing students/users enrolled to course '''
    required_fields = ["id", "email", "username",]

class CourseEnrollmentList(JsonObject):
    object_map = {
        "enrollments": CourseEnrollment
    }

class CourseTab(JsonObject):
    required_fields = ["name"]

class CourseTabs(JsonObject):
    object_map = {
        "tabs": CourseTab
    }

class CourseContentGroup(JsonObject):
    required_fields = ["group_id", "course_id", "content_id"]

    def __unicode__(self):
        return "group {} in course {}".format(self.group_id, self.course_id)
