''' Objects for courses built from json responses from API '''
import datetime

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
        if hasattr(self, 'start_date'):
            return "{} {}".format(
                _("Available"),
                self.start_date.strftime('%B %d, %Y')
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
    def has_future_start_date(self):
        if hasattr(self, 'start_date'):
            current_time = datetime.datetime.now()
            return not (date <= current_time)
        return False

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
