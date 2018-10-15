''' Objects for courses built from json responses from API '''
import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from util.data_sanitizing import sanitize_data, clean_xss_characters
from .json_object import CategorisedJsonObject, JsonObject, DataOnly


# Create your models here.

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods

class _HasCourseDates(CategorisedJsonObject):
    date_fields = ["due", "start"]

    def _fetch_date(self, date_name):
        own_date = getattr(self, date_name, None)
        if not own_date is None:
            return own_date

        if not hasattr(self, "children"):
            return None

        last_child_date = None
        for ch in self.children:
            child_date = ch._fetch_date(date_name)
            if not child_date is None:
                if last_child_date is None or child_date > last_child_date:
                    last_child_date = child_date

        return last_child_date

    def _fetch_date_string(self, date_name):
        fetched_date = self._fetch_date(date_name)
        if fetched_date is None:
            return "-"
        return fetched_date.strftime(settings.DATE_DISPLAY_FORMAT)

    @property
    def due_upon(self):
        return self._fetch_date_string("due")

    @property
    def due_date(self):
        return self._fetch_date("due")

    @property
    def start_upon(self):
        return self._fetch_date_string("start")

    @property
    def start_date(self):
        return self._fetch_date("start")

    @property
    def is_started(self):
        return self.start_date <= datetime.datetime.today()


class Page(_HasCourseDates):

    ''' object representing a page / module within a subsection '''
    required_fields = ["id", "name", ]

    def vertical_usage_id(self):
        return self.id.replace('/', ';_')

    def child_category_list(self):
        if not hasattr(self, "children"):
            return []

        return [child.category for child in self.children]


class Sequential(_HasCourseDates):

    ''' object representing a subsection within a chapter / lesson '''
    required_fields = ["id", "name", ]


class Chapter(_HasCourseDates):

    ''' object representing a chapter / lesson within a course '''
    required_fields = ["id", "name", ]


class Course(CategorisedJsonObject):

    ''' object representing a course '''
    required_fields = ["id", "name", ]
    date_fields = ["start", "end",]

    @property
    def display_id(self):
        return self.id

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
    def formatted_end_date(self):
        if hasattr(self, 'end') and not self.end is None:
            return "{} {}".format(
                _("Available"),
                self.end.strftime(settings.DATE_DISPLAY_FORMAT)
            )
        return None

    @property
    def short_end_date(self):
        if hasattr(self, 'end') and not self.end is None:
            return self.end.strftime(settings.SHORT_DATE_FORMAT)
        return None

    @property
    def formatted_time_span(self):
        start = end = ''
        if hasattr(self, 'start') and not self.start is None:
            start = self.start.strftime(settings.SHORT_DATE_FORMAT)
        if hasattr(self, 'end') and not self.end is None:
            end = self.end.strftime(settings.SHORT_DATE_FORMAT)
        return "{} - {}".format(
            start, end
        )

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

    @property
    def week(self):
        if not getattr(self, 'start', None) is None:
            today = datetime.datetime.today()
            monday1 = (self.start - datetime.timedelta(days=self.start.weekday()))
            monday2 = (today - datetime.timedelta(days=today.weekday()))
            week = ((monday2 - monday1).days / 7) + 1
            if week < 1:
                return None
            return week
        return None

    @property
    def status(self):
        if self.ended:
            return _("COURSE_ENDED")
        elif self.started:
            return _("COURSE_STARTED")
        else:
            return _("COURSE_UNAVAILABLE")

    @property
    def is_evergreen(self):
        if hasattr(self, 'course_run'):
            return False
        for lesson in self.chapters:
            due_dates = [sequential.due for sequential in lesson.sequentials if sequential.due != None]
            if len(due_dates) > 0:
                return False
        return True

    @property
    def has_group_work(self):
        return len(self.group_projects) > 0

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
                    if hasattr(page, 'children'):
                        components.extend([child.id for child in page.children
                                           if child.category not in filter_out_categories])
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
            lesson = self.get_lesson(lesson_id)
            for sequential in lesson.sequentials:
                if len([module for module in sequential.pages if module.id == module_id]) > 0:
                    return sequential
        except:
            return None

    def get_lesson(self, lesson_id):
        try:
            lesson = [lesson for lesson in self.chapters if lesson.id == lesson_id][0]
            return lesson
        except:
            return None

    def get_module(self, lesson_id, module_id):
        try:
            lesson = self.get_lesson(lesson_id)
            for sequential in lesson.sequentials:
                module = [module for module in sequential.pages if module.id == module_id]
                if len(module) > 0:
                    return module[0]
                return None
        except:
            return None

    def inject_basic_data(self):
        for idx, lesson in enumerate(self.chapters, start=1):
            lesson.index = idx
            lesson.navigation_url = '/courses/{}/lessons/{}'.format(self.id, lesson.id)
            for sequential in lesson.sequentials:
                for idx, module in enumerate(sequential.pages, start=1):
                    module.index = idx
                    module.navigation_url = '{}/module/{}'.format(lesson.navigation_url, module.id)
        return self

    def lessons_by_week(self):
        weeks = {}
        no_due_date = {
            "lessons": [],
            "group_activities": [],
        }

        if hasattr(self, 'course_run'):
            for group in self.course_run:
                week_start = datetime.datetime.strptime(group['start_date'], '%m/%d/%Y')
                week_end = datetime.datetime.strptime(group['end_date'], '%m/%d/%Y')
                run_key = week_end.strftime("%d%m%Y")
                weeks[run_key] = {
                    "start": week_start.strftime("%m/%d"),
                    "end": week_end.strftime("%m/%d"),
                    "start_date": week_start,
                    "end_date": week_end,
                    "lessons": [],
                    "group_activities": [],
                    "grouped": group['lessons'],
                }

        for lesson in self.chapters:
            appended = None
            due_dates = [sequential.due for sequential in lesson.sequentials if sequential.due != None]

            for key, week in weeks.iteritems():
                if lesson.index in week['grouped']:
                    week["lessons"].append(lesson)
                    appended = True

            if not appended:
                for key, week in weeks.iteritems():
                    if len(due_dates) > 0 and not appended:
                        due_date = max(sequential.due for sequential in lesson.sequentials if sequential.due != None)
                        if week["start_date"] <= due_date <= week["end_date"]:
                            week["lessons"].append(lesson)
                            appended = True

            if not appended:
                due_dates = [sequential.due for sequential in lesson.sequentials if sequential.due != None]
                if len(due_dates) == 0:
                    no_due_date["lessons"].append(lesson)
                else:
                    due_date = max(sequential.due for sequential in lesson.sequentials if sequential.due != None)
                    due_date = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    if due_date.weekday() == 0:
                        week_start = due_date - datetime.timedelta(days=due_date.weekday() - 1, weeks=1)
                    else:
                        week_start = due_date - datetime.timedelta(days=due_date.weekday() - 1)
                    week_end = week_start + datetime.timedelta(days=6)
                    lesson_key = week_end.strftime("%d%m%Y")

                    if lesson_key in weeks:
                        weeks[lesson_key]["lessons"].append(lesson)
                    else:
                        weeks[lesson_key] = {
                            "start": week_start.strftime("%m/%d"),
                            "end": week_end.strftime("%m/%d"),
                            "start_date": week_start,
                            "end_date": week_end,
                            "lessons": [lesson],
                            "group_activities": [],
                            "grouped": [],
                        }

        if getattr(self, 'group_work_enabled', None):
            for project in self.group_projects:
                for activity in project.activities:
                    if activity.due:
                        activity.due_on = activity.due.strftime("%B %e")
                    if activity.due == None or len(weeks.values()) == 0:
                        no_due_date["has_group"] = True
                        no_due_date["group_activities"].append(activity)
                    else:
                        due_date = activity.due.replace(hour=0, minute=0, second=0, microsecond=0)
                        if due_date.weekday() == 0:
                            week_start = due_date - datetime.timedelta(days=due_date.weekday() - 1, weeks=1)
                        else:
                            week_start = due_date - datetime.timedelta(days=due_date.weekday() - 1)
                        week_end = week_start + datetime.timedelta(days=6)
                        group_key = week_end.strftime("%d%m%Y")
                        activity.due_on = activity.due.strftime("%B %e")
                        appended = None

                        for key, week in weeks.iteritems():
                            if week["start_date"] <= due_date <= week["end_date"]:
                                week["has_group"] = True
                                week["group_activities"].append(activity)
                                appended = True

                        if not appended:
                            if group_key in weeks:
                                weeks[group_key]["has_group"] = True
                                weeks[group_key]["group_activities"].append(activity)
                            else:
                                weeks[group_key] = {
                                    "start": week_start.strftime("%m/%d"),
                                    "end": week_end.strftime("%m/%d"),
                                    "start_date": week_start,
                                    "end_date": week_end,
                                    "has_group": True,
                                    "group_only": True,
                                    "lessons": [],
                                    "group_activities": [activity],
                                    "grouped": [],
                                }

        weeks = sorted(weeks.values(), key=lambda w: w["end_date"])
        if len(no_due_date["lessons"]) > 0 or len(no_due_date["group_activities"]) > 0:
            weeks.append(no_due_date)

        for idx, week in enumerate(weeks, start=1):
            week["index"] = idx
        return weeks

    def graded_items(self):
        graded_items = {
            "modules": [],
            "group_activities": [],
        }
        graded_lessons = [lesson for lesson in self.chapters if getattr(lesson, 'assesment_score', None) != None]
        for lesson in graded_lessons:
            for sequential in lesson.sequentials:
                if sequential.name.find('Assessment') != -1:
                    for module in sequential.pages:
                        is_assesment = module.name.find('Assessment') != -1
                        if is_assesment:
                            module.lesson_name = lesson.name
                            module.assesment_score = lesson.assesment_score
                            graded_items["modules"].append(module)

        if getattr(self, 'group_work_enabled', None):
            for project in self.group_projects:
                for activity in project.activities:
                    if activity.is_graded:
                        graded_items["group_activities"].append(activity)

        return graded_items

    def _validate_fields(self, dictionary):
        super(Course, self)._validate_fields(dictionary)

        # applying xss data cleaning
        sanitize_data(
            data=dictionary, props_to_clean=settings.COURSE_PROPERTIES_TO_CLEAN,
            clean_methods=(clean_xss_characters,)
        )


class CourseListCourse(JsonObject):
    required_fields = ["course_id", "display_name", ]

    @property
    def display_id(self):
        return self.course_id


class CourseList(JsonObject):
    object_map = {
        "courses": CourseListCourse
    }


class CourseEnrollment(JsonObject):
    ''' object representing students/users enrolled to course '''
    required_fields = ["id", "email", "username"]


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
        return _("group {group_id} in course {course_id}").format(
            group_id=self.group_id,
            course_id=self.course_id
        )


class CourseMetrics(JsonObject):
    object_map = {
        "grade_cutoffs": DataOnly
    }


class CourseTimeSeriesMetrics(JsonObject):
    object_map = {
        'active_users': DataOnly,
        'modules_completed': DataOnly,
        'users_completed': DataOnly,
        'users_enrolled': DataOnly,
        'users_not_started': DataOnly,
        'users_started': DataOnly,
    }


class CourseBlockData(JsonObject):
    required_fields = ['id', 'block_id', 'type']

    def is_complete(self):
        return hasattr(self, 'completion') and self.completion == 1.0


class UserCourseEnrollment(JsonObject):
    """
    Data structure linking a user and a course they are enrolled in.
    """
    required_fields = ['created', 'mode', 'is_active', 'user', 'course_id']


class CourseCohortSettings(JsonObject):
    """
    Data structure to hold the cohort settings of a course.
    """
    required_fields = ['id', 'is_cohorted']
