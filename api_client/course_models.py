''' Objects for courses built from json responses from API '''
import datetime
import math

from django.utils.translation import ugettext as _

from .json_object import CategorisedJsonObject, JsonObject

# Create your models here.

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods


class Page(CategorisedJsonObject):

    ''' object representing a page / module within a subsection '''
    required_fields = ["id", "name", ]

    def vertical_usage_id(self):
        return self.id.replace('/', ';_')

    def child_category_list(self):
        if not hasattr(self, "children"):
            return []

        return [child.category for child in self.children]


class Sequential(CategorisedJsonObject):

    ''' object representing a subsection within a chapter / lesson '''
    required_fields = ["id", "name", ]


class Chapter(CategorisedJsonObject):

    ''' object representing a chapter / lesson within a course '''
    required_fields = ["id", "name", ]


class Course(CategorisedJsonObject):

    ''' object representing a course '''
    required_fields = ["id", "name", ]

    @property
    def nav_url(self):
        return '/courses/{}'.format(self.id)

    @property
    def formatted_start_date(self):
        if hasattr(self, 'start'):
            return "{} {}".format(
                _("Available"),
                self.start.strftime('%B %d, %Y')
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
        if hasattr(self, 'start'):
            date = self.start
            current_time = datetime.datetime.now()
            return (date <= current_time)
        return True

    @property
    def days_till_start(self):
        if hasattr(self, 'start'):
            course_start = datetime.datetime.strptime(self.start, '%Y-%m-%dT%H:%M:%SZ')
            days = str(
                int(math.floor(((course_start - datetime.datetime.today()).total_seconds()) / 3600 / 24)))
            return days
        return 0



    def module_count(self):
        module_count = 0
        for chapter in self.chapters:
            for sequential in chapter.sequentials:
                module_count += len(sequential.children)

        return module_count

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
