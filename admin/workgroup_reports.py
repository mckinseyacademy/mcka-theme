import datetime
import copy

from django.conf import settings
from django.utils.translation import ugettext as _

from lib.util import DottableDict
from api_client.project_models import Project
from api_client import course_api, user_api, group_api
from api_client.organization_models import Organization

from .controller import load_course
from .models import WorkGroup
from .models import WorkGroupActivityXBlock

COMPLETION_STAGES = ['upload', 'evaluation', 'grade']

IRRELEVANT = '--'
NOT_APPLICABLE = _('n/a')

BLANK_ACTIVITY = DottableDict({
    "name": _("This activity does not exist"),
    "grade_type": None,
    "upload_date": NOT_APPLICABLE,
    "evaluation_date": NOT_APPLICABLE,
    "grade_date": NOT_APPLICABLE,
})

BLANK_ACTIVITY_STATUS = DottableDict({
    "upload": "irrelevant",
    "evaluation": "irrelevant",
    "ta_graded": False,
    "grade": "irrelevant",
    "graded": "irrelevant",
    "review_groups": [],
})


class WorkgroupCompletionData(object):
    projects = None
    completions = None
    course = None
    workgroup_id = None

    project_workgroups = {}
    project_activities = {}
    user_review_assignments = {}

    activity_xblocks = {}

    def _get_activity_xblock(self, activity_id):
        if activity_id not in self.activity_xblocks:
            self.activity_xblocks[activity_id] = WorkGroupActivityXBlock.fetch_from_activity(self.course.id,
                                                                                             activity_id)
        return self.activity_xblocks[activity_id]

    def __init__(self, course_id, group_id=None, restrict_to_users_ids=None):
        self.activity_xblocks = {}
        self.course = load_course(course_id)
        self.restrict_to_users_ids = restrict_to_users_ids
        self.group_project_lookup = {gp.id: gp for gp in self.course.group_projects}

        if group_id is None:
            self.projects = [
                p for p in Project.fetch_projects_for_course(course_id) if p.content_id in self.group_project_lookup
            ]
        else:
            self.workgroup_id = int(group_id)
            self.projects = [Project.fetch(WorkGroup.fetch(self.workgroup_id).project)]

        self._load(course_id)


    @staticmethod
    def _make_completion_key(content_id, user_id, stage):
        format_string = '{}_{}' if stage is None else '{}_{}_{}'
        return format_string.format(content_id, user_id, stage)

    def is_complete(self, group_xblock, user_id, stage=None):
        if stage == 'grade' and group_xblock.ta_graded:
            return None

        return WorkgroupCompletionData._make_completion_key(group_xblock.id, user_id, stage) in self.completions

    def is_group_complete(self, group_xblock, user_ids, stage=None):
        if stage == 'grade' and group_xblock.ta_graded:
            return None

        complete = True
        for u_id in user_ids:
            complete = complete and self.is_complete(group_xblock, u_id, stage)
            if not complete:
                return False
        return complete

    def _load_project_workgroup_status(self, project, pw):
        for u in pw.users:
            for a in self.project_activities[project.id]:
                group_xblock = self._get_activity_xblock(a.id)
                assignment_groups = user_api.get_user_groups(u.id, group_type='reviewassignment',
                                                             data__xblock_id=group_xblock.id)
                review_assignments = [wg for ag in assignment_groups for wg in group_api.get_workgroups_in_group(ag.id)]
                if u.id not in self.user_review_assignments:
                    self.user_review_assignments[u.id] = {}
                self.user_review_assignments[u.id][group_xblock.id] = [
                    self.project_workgroups[project.id][ra.id]
                    for ra in review_assignments if
                    ra.id in self.project_workgroups[project.id]
                ]

    def _load(self, course_id):
        completion_data = course_api.get_course_completions(course_id)
        self.completions = {
            WorkgroupCompletionData._make_completion_key(c.content_id, c.user_id, c.stage): c for c in completion_data
        }

        for project in self.projects:
            if project.organization:
                organization = Organization.fetch(project.organization)
                project.organization_name = organization.display_name
            self.project_workgroups[project.id] = {w_id:WorkGroup.fetch_with_members(w_id) for w_id in project.workgroups}
            group_project = [gp for gp in self.course.group_projects if gp.id == project.content_id][0]
            project.name = group_project.name
            self.project_activities[project.id] = group_project.activities

            # load up user review assignments
            if self.workgroup_id:
                self._load_project_workgroup_status(project, self.project_workgroups[project.id][self.workgroup_id])
            else:
                for k, pw in self.project_workgroups[project.id].iteritems():
                    self._load_project_workgroup_status(project, pw)

    def is_workgroup_activity_complete(self, workgroup, xblock):
        user_ids = [u.id for u in workgroup.members]
        return self.is_group_complete(xblock, user_ids)

    def _review_link(self, workgroup, activity=None):
        if activity:
            return "/courses/{}/group_work/{}?actid={}".format(
                self.course.id,
                workgroup.id,
                activity.id,
            )
        return "/courses/{}/group_work/{}".format(
            self.course.id,
            workgroup.id,
        )

    def build_report_data(self):
        total_group_count = 0
        projects = []
        for p in self.projects:
            project_data = self.get_v1_data(p)
            total_group_count += p.group_count
            projects.append(project_data)

        return {
            "projects": projects,
            "course": self.course,
            "total_group_count": total_group_count,
        }

    def get_v1_data(self, p):

        def get_due_date(group_xblock, date_name):
            if hasattr(group_xblock, "milestone_dates"):
                return getattr(group_xblock.milestone_dates, date_name, None)
            return None

        def formatted_milestone_date(group_xblock, date_name):
            date_value = get_due_date(group_xblock, date_name)
            if date_value is None:
                return IRRELEVANT
            return date_value.strftime(settings.SHORT_DATE_FORMAT)

        def report_completion_boolean(bool_value, due_date=None):
            if bool_value is None:
                return 'irrelevant'
            if bool_value:
                return 'complete'
            elif due_date and due_date > datetime.datetime.now():
                return 'incomplete'
            return 'incomplete overdue'

        individual_stages = ['evaluation', 'grade']

        # only take the first 3 activities
        p.activities = self.project_activities[p.id][0:3]
        p.workgroups = [self.project_workgroups[p.id][self.workgroup_id]] if self.workgroup_id else [
            g for k, g in self.project_workgroups[p.id].iteritems()
            ]
        p.group_count = len(p.workgroups)

        for a in p.activities:
            group_xblock = self._get_activity_xblock(a.id)
            a.upload_date = formatted_milestone_date(group_xblock, "upload")
            a.evaluation_date = formatted_milestone_date(group_xblock, "evaluation")
            a.grade_date = formatted_milestone_date(group_xblock, "grade")
            a.grade_type = _("TA Graded") if group_xblock.ta_graded else _("Peer Graded")
            if self.workgroup_id and group_xblock.ta_graded:
                a.review_link = self._review_link(p.workgroups[0], a)
        remove_groups = set()
        for g in p.workgroups:
            if self.restrict_to_users_ids is not None:
                g.users = [user for user in g.users if user.id in self.restrict_to_users_ids]

            if not g.users:
                remove_groups.add(g.id)
                continue

            g.review_link = self._review_link(g)
            user_ids = [u.id for u in g.users]
            g.activity_statuses = []
            for a in p.activities:
                group_xblock = self._get_activity_xblock(a.id)
                activity_status = DottableDict(
                    {
                        s: report_completion_boolean(
                            self.is_group_complete(group_xblock, user_ids, s),
                            get_due_date(group_xblock, s)
                        )
                        for s in COMPLETION_STAGES
                        }
                )
                activity_status.ta_graded = group_xblock.ta_graded
                activity_status.review_link = self._review_link(g, a)
                activity_status.graded = report_completion_boolean(
                    self.is_group_complete(group_xblock, user_ids), get_due_date(group_xblock, 'grade')
                )
                activity_status.modifier_class = activity_status.graded

                g.activity_statuses.append(activity_status)

            while len(g.activity_statuses) < 3:
                g.activity_statuses.append(BLANK_ACTIVITY_STATUS)

            for u in g.users:
                u.activity_statuses = []
                u.max_review_count = 0
                if self.workgroup_id:
                    organizations = user_api.get_user_organizations(u.id)
                    u.company = organizations[0].display_name if len(organizations) > 0 else None
                for a in p.activities:
                    group_xblock = self._get_activity_xblock(a.id)
                    user_activity_status = DottableDict(
                        {
                            s: report_completion_boolean(
                                self.is_complete(group_xblock, u.id, s),
                                get_due_date(group_xblock, s)
                            )
                            for s in individual_stages
                            }
                    )
                    user_activity_status.upload = IRRELEVANT
                    user_activity_status.review_groups = self.user_review_assignments[u.id][group_xblock.id]
                    if len(user_activity_status.review_groups) > u.max_review_count:
                        u.max_review_count = len(user_activity_status.review_groups)
                    idx = 0
                    for review_group in user_activity_status.review_groups:
                        review_group.index = idx
                        idx += 1
                        review_group.review_link = self._review_link(review_group, a)
                        review_group.modifier_class = report_completion_boolean(
                            self.is_workgroup_activity_complete(review_group, group_xblock),
                            get_due_date(group_xblock, 'grade'))

                    u.activity_statuses.append(user_activity_status)

                while len(u.activity_statuses) < 3:
                    u.activity_statuses.append(BLANK_ACTIVITY_STATUS)

                u.review_row_count = u.max_review_count if u.max_review_count > 0 else 1
                u.review_row_indexer = range(0, u.review_row_count)
        p.workgroups = [workgroup for workgroup in p.workgroups if workgroup.id not in remove_groups]
        while len(p.activities) < 3:
            # Need copy here, because we assign different indexes below
            p.activities.append(copy.copy(BLANK_ACTIVITY))
        act_idx = 0
        for activity in p.activities:
            act_idx += 1
            activity.index = act_idx
        return p


def generate_workgroup_csv_report(course_id, url_prefix, restrict_to_users_ids=None):
    output_lines = []

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    wcd = WorkgroupCompletionData(course_id, restrict_to_users_ids=restrict_to_users_ids)

    for project in wcd.build_report_data()["projects"]:
        if project.organization:
            organization = Organization.fetch(project.organization)
            project.organization_name = organization.display_name
        output_line([project.name])

        activity_names_row = ["", ""]
        for activity in project.activities:
            activity_names_row.extend(["", activity.name, "", "", ""])
        output_line(activity_names_row)

        group_header_row = ["Group", ""]
        for activity in project.activities:
            group_header_row.extend(["Upload", "Evaluation", "Review", "Review Groups", "Graded"])
        output_line(group_header_row)

        for workgroup in project.workgroups:
            workgroup_row = [workgroup.name, ""]
            for activity_status in workgroup.activity_statuses:
                workgroup_row.extend([activity_status.upload, activity_status.evaluation])
                grade_value = activity_status.grade
                if activity_status.ta_graded:
                    grade_value = "TA Graded{} ({})".format(
                        "*" if activity_status.modifier_class == "incomplete" else "",
                        "{}{}".format(url_prefix, activity_status.review_link),
                    )
                workgroup_row.extend([grade_value, "", activity_status.graded])
            output_line(workgroup_row)

            for user in workgroup.users:
                user_row = ["", user.username]
                for user_activity_status in user.activity_statuses:
                    user_row.extend(
                        [user_activity_status.upload, user_activity_status.evaluation, user_activity_status.grade])
                    review_group_data = []
                    for review_group in user_activity_status.review_groups:
                        review_group_data.append("{}{} ({})".format(
                            review_group.name,
                            "*" if review_group.modifier_class == "incomplete" else "",
                            "{}{}".format(url_prefix, review_group.review_link),
                        )
                        )
                    user_row.extend(['; '.join(review_group_data), "--"])
                output_line(user_row)

        output_line("--------")

    return '\n'.join(output_lines)
