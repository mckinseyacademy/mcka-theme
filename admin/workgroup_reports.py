from django.utils.translation import ugettext as _

from lib.util import DottableDict
from api_client.project_models import Project
from api_client import course_api, user_api, group_api

from .controller import load_course
from .controller import get_group_project_activities
from .models import WorkGroup
from .models import WorkGroupActivityXBlock

COMPLETION_STAGES = ['upload', 'evaluation', 'grade']


class WorkgroupCompletionData(object):

    projects = None
    completions = None
    course = None

    project_workgroups = {}
    project_activities = {}
    user_review_assignments = {}

    activity_xblocks = {}
    def _get_activity_xblock(self, activity_id):
        if activity_id not in self.activity_xblocks:
            self.activity_xblocks[activity_id] = WorkGroupActivityXBlock.fetch_from_activity(self.course.id, activity_id)
        return self.activity_xblocks[activity_id]

    def __init__(self, course_id):
        self.load_for_course(course_id)

    @staticmethod
    def _make_completion_key(content_id, user_id, stage):
        format_string = '{}_{}' if stage is None else '{}_{}_{}'
        return format_string.format(content_id, user_id, stage)

    def is_complete(self, group_xblock, user_id, stage=None):
        if stage=='grade' and group_xblock.ta_graded:
            return None

        return WorkgroupCompletionData._make_completion_key(group_xblock.id, user_id, stage) in self.completions

    def is_group_complete(self, group_xblock, user_ids, stage=None):
        if stage=='grade' and group_xblock.ta_graded:
            return None

        complete = True
        for u_id in user_ids:
            complete = complete and self.is_complete(group_xblock, u_id, stage)
            if not complete:
                return False
        return complete

    def load_for_course(self, course_id):
        self.projects = Project.fetch_projects_for_course(course_id)
        completion_data = course_api.get_course_completions(course_id)
        self.completions = {WorkgroupCompletionData._make_completion_key(c.content_id, c.user_id, c.stage) : c for c in completion_data}
        self.course = load_course(course_id)

        for project in self.projects:
            self.project_workgroups[project.id] = {w_id:WorkGroup.fetch_with_members(w_id) for w_id in project.workgroups}
            group_project = [ch for ch in self.course.group_project_chapters if ch.id == project.content_id][0]
            project.name = group_project.name
            self.project_activities[project.id] = get_group_project_activities(group_project)

            # load up user review assignments
            for k, pw in self.project_workgroups[project.id].iteritems():
                for u in pw.users:
                    for a in self.project_activities[project.id]:
                        group_xblock = self._get_activity_xblock(a.id)
                        assignment_groups = user_api.get_user_groups(u.id, group_type='reviewassignment', data__xblock_id=group_xblock.id)
                        review_assignments = [wg for ag in assignment_groups for wg in group_api.get_workgroups_in_group(ag.id)]
                        if u.id not in self.user_review_assignments:
                            self.user_review_assignments[u.id] = {}
                        self.user_review_assignments[u.id][group_xblock.id] = [self.project_workgroups[project.id][ra.id] for ra in review_assignments]


    def is_workgroup_activity_complete(self, workgroup, xblock):
        user_ids = [u.id for u in workgroup.members]
        return self.is_group_complete(xblock, user_ids)

    def _report_completion_boolean(self, bool_value):
        if bool_value is None:
            return "--"
        return _('complete') if bool_value else _('incomplete')

    def _review_link(self, workgroup, activity):
        return "/courses/{}/group_work/{}?seqid={}".format(
            self.course.id,
            workgroup.id,
            activity.id
        )

    def build_report_data(self):

        individual_stages = ['evaluation', 'grade']

        for p in self.projects:
            p.activities = self.project_activities[p.id]
            p.workgroups = [g for k, g in self.project_workgroups[p.id].iteritems()]

            for g in p.workgroups:
                user_ids = [u.id for u in g.users]
                g.activity_statuses = []
                for a in p.activities:
                    group_xblock = self._get_activity_xblock(a.id)
                    activity_status = DottableDict(
                        {
                            s:self._report_completion_boolean(self.is_group_complete(group_xblock, user_ids, s)) for s in COMPLETION_STAGES
                        }
                    )
                    activity_status.ta_graded = group_xblock.ta_graded
                    activity_status.review_link = self._review_link(g, a)
                    activity_status.modifier_class = _("complete") if self.is_group_complete(group_xblock, user_ids) else _("incomplete")

                    g.activity_statuses.append(activity_status)

                for u in g.users:
                    u.activity_statuses = []
                    for a in p.activities:
                        group_xblock = self._get_activity_xblock(a.id)
                        user_activity_status = DottableDict(
                            {
                                s:self._report_completion_boolean(self.is_complete(group_xblock, u.id, s)) for s in individual_stages
                            }
                        )
                        user_activity_status.upload = "--"
                        user_activity_status.review_groups = self.user_review_assignments[u.id][group_xblock.id]
                        for review_group in user_activity_status.review_groups:
                            review_group.review_link = self._review_link(review_group, a)
                            review_group.modifier_class = _("complete") if self.is_workgroup_activity_complete(review_group, group_xblock) else _("incomplete")

                        u.activity_statuses.append(user_activity_status)

        return {
            "projects": self.projects,
            "course": self.course,
        }

def generate_workgroup_csv_report(course_id, url_prefix):

    output_lines = []

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    wcd = WorkgroupCompletionData(course_id)

    for project in wcd.build_report_data()["projects"]:
        output_line([project.name])

        activity_names_row = ["",""]
        for activity in project.activities:
            activity_names_row.extend(["",activity.name,"",""])
        output_line(activity_names_row)

        group_header_row = ["Group",""]
        for activity in project.activities:
            group_header_row.extend(["Upload","Evaluation","Grade"])
        output_line(group_header_row)

        for workgroup in project.workgroups:
            workgroup_row = [workgroup.name,""]
            for activity_status in workgroup.activity_statuses:
                workgroup_row.extend([activity_status.upload,activity_status.evaluation])
                grade_value = activity_status.grade
                if activity_status.ta_graded:
                    grade_value = "TA Graded{} ({})".format(
                        "*" if activity_status.modifier_class=="incomplete" else "",
                        "{}{}".format(url_prefix, activity_status.review_link),
                    )
                workgroup_row.extend([grade_value,""])
            output_line(workgroup_row)

            for user in workgroup.users:
                user_row = ["",user.username]
                for user_activity_status in user.activity_statuses:
                    user_row.extend([user_activity_status.upload,user_activity_status.evaluation,user_activity_status.grade])
                    review_group_data = []
                    for review_group in user_activity_status.review_groups:
                        review_group_data.append("{}{} ({})".format(
                              review_group.name,
                              "*" if review_group.modifier_class=="incomplete" else "",
                                "{}{}".format(url_prefix, review_group.review_link),
                            )
                        )
                    user_row.append('; '.join(review_group_data))
                output_line(user_row)

        output_line("--------")

    return '\n'.join(output_lines)
