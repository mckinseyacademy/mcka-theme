from django.utils.translation import ugettext as _

from api_client.project_models import Project
from api_client import course_api, user_api, group_api

from .controller import load_course
from .models import WorkGroup

COMPLETION_STAGES = ['upload', 'evaluation', 'grade']


class WorkgroupCompletionData(object):

    projects = None
    completions = None
    course = None

    project_workgroups = {}
    project_activities = {}
    user_completions = {}
    user_review_assignments = {}

    def __init__(self, course_id):
        self.load_for_course(course_id)

    @staticmethod
    def _make_completion_key(content_id, user_id, stage):
        format_string = '{}_{}' if stage is None else '{}_{}_{}'
        return format_string.format(content_id, user_id, stage)

    def is_complete(self, content_id, user_id, stage=None):
        return WorkgroupCompletionData._make_completion_key(content_id, user_id, stage) in self.completions

    def is_group_complete(self, content_id, user_ids, stage=None):
        complete = True
        for u_id in user_ids:
            complete = complete and self.is_complete(content_id, u_id, stage)
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
            self.project_activities[project.id] = [s for s in group_project.sequentials if len(s.pages) > 0 and "group-project" in s.pages[0].child_category_list()]

            # by user completion data
            for k, pw in self.project_workgroups[project.id].iteritems():
                for u in pw.users:
                    self.user_completions[u.id] = {}
                    user_comp = [c for c in completion_data if c.user_id == u.id]
                    for a in self.project_activities[project.id]:
                        self.user_completions[u.id][a.id] = {}
                        for s in COMPLETION_STAGES:
                            gp_id = a.pages[0].children[0].id
                            self.user_completions[u.id][a.id][s] = self.is_complete(gp_id, u.id, s)

                    assignment_groups = user_api.get_user_groups(u.id, group_type = 'reviewassignment')
                    review_assignments = [wg for ag in assignment_groups for wg in group_api.get_workgroups_in_group(ag.id)]
                    self.user_review_assignments[u.id] = [self.project_workgroups[project.id][ra.id] for ra in review_assignments]


def generate_workgroup_csv_report(course_id, url_prefix):
    output_lines = []
    individual_stages = ['evaluation', 'grade']

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    def report_completion_boolean(bool_value):
        return _('complete') if bool_value else _('incomplete')

    wcd = WorkgroupCompletionData(course_id)

    def is_workgroup_activity_complete(workgroup, activity_id):
        user_ids = [u.id for u in workgroup.members]
        return wcd.is_group_complete(activity_id, user_ids)

    for p in wcd.projects:
        activities = wcd.project_activities[p.id]
        workgroups = wcd.project_workgroups[p.id]

        # project header
        output_line([p.name])

        # group headers
        activity_headers = [a.name for a in activities]
        activity_header_row = ['','']
        for ah in activity_headers:
            activity_header_row.extend(['',ah,'',''])
        output_line(activity_header_row)
        group_header_row = ['Group', '']
        for ah in activity_headers:
            group_header_row.extend(['Upload', 'Evalulation', 'Grade', ''])
        output_line(group_header_row)

        # group data
        for k, g in workgroups.iteritems():
            # group summary
            group_summary_row = [g.name, '']
            for a in activities:
                gp_id = a.pages[0].children[0].id
                for s in COMPLETION_STAGES:
                    user_ids = [u.id for u in g.users]
                    complete = wcd.is_group_complete(gp_id, user_ids, s)
                    group_summary_row.append(report_completion_boolean(complete))
                group_summary_row.append('')
            output_line(group_summary_row)

            # group user detail
            for member in g.members:
                user_row = ['', member.username]
                for a in activities:
                    gp_id = a.pages[0].children[0].id
                    for s in COMPLETION_STAGES:
                        if member.id in wcd.user_completions:
                            v = report_completion_boolean(wcd.user_completions[member.id][a.id][s]) if s in individual_stages else '--'
                        else:
                            v = report_completion_boolean(False)
                        user_row.append(v)

                    review_groups = []
                    for wg in wcd.user_review_assignments[member.id]:
                        review_groups.append(
                            "{}{} ({})".format(
                                wg.name,
                                "" if is_workgroup_activity_complete(wg, gp_id) else "*",
                                "{}/courses/{}/group_work/{}?seqid={}".format(
                                    url_prefix,
                                    course_id,
                                    wg.id,
                                    a.id
                                )
                            )
                        )
                    user_row.append("; ".join(review_groups))

                output_line(user_row)

    return '\n'.join(output_lines)
